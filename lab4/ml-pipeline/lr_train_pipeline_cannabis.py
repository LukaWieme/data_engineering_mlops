import kfp
import typing
import argparse
from typing import Dict
from typing import NamedTuple
from kfp import dsl
from kfp.dsl import (Artifact,
                        Dataset,
                        Input,
                        Model,
                        Output,
                        Metrics,
                        ClassificationMetrics,
                        component,
                        OutputPath,
                        InputPath)
import google.cloud.aiplatform as aip
from google_cloud_pipeline_components.v1.model import ModelUploadOp
from google_cloud_pipeline_components.v1.endpoint import (EndpointCreateOp,ModelDeployOp)
from google_cloud_pipeline_components.types import artifact_types


@dsl.component(
    packages_to_install=["pandas", "scikit-learn==1.3.2"],
    base_image="python:3.10.7-slim"
)
def train_test_split(dataset: Input[Dataset], dataset_train: Output[Dataset], dataset_test: Output[Dataset]):
    '''train_test_split'''
    import pandas as pd
    import logging
    import sys
    from sklearn.model_selection import train_test_split as tts

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    alldata = pd.read_csv(dataset.path, index_col=None)
    train, test = tts(alldata, test_size=0.3, random_state=42, stratify=alldata["class"])
    train.to_csv(dataset_train.path + ".csv", index=False, encoding='utf-8-sig')
    test.to_csv(dataset_test.path + ".csv", index=False, encoding='utf-8-sig')


@dsl.component(
    packages_to_install=["pandas", "scikit-learn==1.3.2"],
    base_image="python:3.10.7-slim"
)
def train_lr(features: Input[Dataset], model: Output[Model]):
    '''train a LogisticRegression with default parameters'''
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    import pickle

    data = pd.read_csv(features.path + ".csv")
    model_lr = LogisticRegression(max_iter=1000, random_state=42)
    model_lr.fit(data.drop('class', axis=1), data['class'])
    model.metadata["framework"] = "LR"
    file_name = model.path + f".pkl"
    with open(file_name, 'wb') as file:
        pickle.dump(model_lr, file)


@dsl.component(
    packages_to_install=[
        "pandas", "scikit-learn==1.3.2", "numpy", "google-cloud-aiplatform"
    ], base_image="python:3.10.7-slim"
)
def lr_model_evaluation(
        project_id: str,
        region: str,
        test_set: Input[Dataset],
        model_lr: Input[Model],
        thresholds_dict_str: str,
        metrics: Output[ClassificationMetrics],
        kpi: Output[Metrics]
) -> NamedTuple('outputs', approval=bool):
    import pandas as pd
    import logging
    from sklearn.metrics import confusion_matrix, accuracy_score
    import sklearn.metrics as skl_metrics
    import json
    import typing
    from numpy import nan_to_num
    from google.cloud import aiplatform
    import pickle
    from numpy import nan_to_num
    from datetime import datetime
    import random
    idn = random.randint(0, 1000)

    def threshold_check(val1, val2):
        cond = False
        if val1 >= val2:
            cond = True
        return cond

    data = pd.read_csv(test_set.path + ".csv")

    # Loading the saved model with joblib
    m_filename = model_lr.path + ".pkl"
    model = pickle.load(open(m_filename, 'rb'))

    y_test = data.drop(columns=["class"])
    y_target = data['class']
    y_pred = model.predict(y_test)

    y_scores = model.predict_proba(data.drop(columns=["class"]))[:, 1]

    metrics.log_confusion_matrix(
        model.classes_.tolist(),
        confusion_matrix(data['class'], y_pred, labels=model.classes_).tolist(),
    )

    accuracy = accuracy_score(data['class'], y_pred)
    thresholds_dict = json.loads(thresholds_dict_str)
    model_lr.metadata["accuracy"] = float(accuracy)
    kpi.log_metric("accuracy", float(accuracy))
    outputs = NamedTuple('outputs', approval=bool)
    approval_value = threshold_check(float(accuracy), float(thresholds_dict['accuracy']))

    # How to start an experiment - just for demonstration
    aiplatform.init(
        project=project_id,
        location=region,
        experiment="cannabis-lr"
    )

    run_id = f"run-{idn}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    aiplatform.start_run(run_id)

    training_metrics = {
        'model_accuracy': skl_metrics.accuracy_score(y_target, y_pred),
        'model_precision': skl_metrics.precision_score(y_target, y_pred, average='macro', zero_division=0),
        'model_recall': skl_metrics.recall_score(y_target, y_pred, average='macro', zero_division=0),
        'model_f1': skl_metrics.f1_score(y_target, y_pred, average='macro', zero_division=0),
        'model_logloss': skl_metrics.log_loss(y_target, model.predict_proba(y_test), labels=model.classes_),
    }
    aiplatform.log_metrics(training_metrics)

    return outputs(approval_value)


@dsl.component(
    packages_to_install=["google-cloud-storage"],
    base_image="python:3.10.7-slim"
)
def upload_model_to_gcs(project_id: str, model_repo: str, model: Input[Model]):
    '''upload model to gsc'''
    from google.cloud import storage
    import logging
    import sys

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # upload the model to GCS
    client = storage.Client(project=project_id)
    bucket = client.bucket(model_repo)
    blob = bucket.blob('model.pkl')
    source_file_name = model.path + '.pkl'

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {model_repo}.")


# Define the workflow of the pipeline.
@kfp.dsl.pipeline(
    name="cannabis-predictor-training-pipeline")
def pipeline(project_id: str, region: str, data_bucket: str, dataset_uri: str, model_repo: str,
             thresholds_dict_str: str, model_repo_uri: str):
    dataset_op = kfp.dsl.importer(
        artifact_uri=dataset_uri,
        artifact_class=Dataset,
        reimport=False,
    )

    train_test_split_op = train_test_split(dataset=dataset_op.output)

    training_lr_job_run_op = train_lr(features=train_test_split_op.outputs["dataset_train"])

    model_evaluation_op = lr_model_evaluation(
        project_id=project_id,
        region=region,
        test_set=train_test_split_op.outputs["dataset_test"],
        model_lr=training_lr_job_run_op.outputs["model"],
        thresholds_dict_str=thresholds_dict_str,
        # I deploy the model anly if the model performance is above the threshold
    )

    with dsl.If(
            model_evaluation_op.outputs["approval"] == True,
            name="approve-model",
    ):
        upload_model_to_gc_op = upload_model_to_gcs(
            project_id=project_id,
            model_repo=model_repo,
            model=training_lr_job_run_op.outputs['model']
        )


def compile_pipeline(target_file):
    compiler.Compiler().compile(pipeline_func=ml_pipeline,
                                package_path=target_file)

# This is only for testing - run the pipeline via CI/CD as we did in Lab4 Live
def _run_pipeline():
    # The Google Cloud project that this pipeline runs in.
    PROJECT_ID = "assignment1-512310"
    # The region that this pipeline runs in
    REGION = "us-central1"
    # Specify a Cloud Storage URI that your pipelines service account can access. The artifacts of your pipeline runs are stored within the pipeline root.
    PIPELINE_ROOT = "drug-temp-group9"
    # Prepare the pipeline job
    job = aip.PipelineJob(
        display_name="cannabis-predictor",
        enable_caching=False,
        template_path="cannabis_prdictor_training_pipeline.yaml",
        pipeline_root=PIPELINE_ROOT,
        location=REGION,
        parameter_values={
            'project_id': PROJECT_ID,  # makesure to use your project id
            'region': REGION,
            'data_bucket': 'drug-data-group9',  # makesure to use your data bucket name
            'dataset_uri': 'gs://drug-data-group9/drug_consumption.csv',
            'model_repo': 'drug-models-group9',  # makesure to use your model bucket name
            'thresholds_dict_str': '{"roc":0.8}',
            'model_repo_uri': 'gs://drug-models-group9'  # makesure to use your model bucket name
        }
    )

    job.run()

def parse_command_line_arguments():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--target_file', type=str, default="training_pipeline.yaml", help="cannabis-predictor")
    args = parser.parse_args()
    return vars(args)


if __name__ == '__main__':
    compile_pipeline(**parse_command_line_arguments())
    # _run_pipeline() - This is only for testing - compile and run the pipeline via CI/CD as we did in Lab4 Live
