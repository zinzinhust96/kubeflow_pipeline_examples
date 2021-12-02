import os
from pathlib import Path
import requests
from kubernetes import client as k8s_client

import kfp

component_url_prefix = '/data_processing/'
test_data_url_prefix = component_url_prefix + 'testdata'

#Prepare input/output paths and data
# input_data_gcs_dir = 'gs://<my bucket>/<path>/'
# output_data_gcs_dir = 'gs://<my bucket>/<path>/'

#Downloading the training set (to upload to GCS later)
# training_set_features_local_path = os.path.join('.', 'training_set_features.tsv')
# training_set_labels_local_path = os.path.join('.', 'training_set_labels.tsv')

# training_set_features_url = test_data_url_prefix + '/training_set_features.tsv'
# training_set_labels_url = test_data_url_prefix + '/training_set_labels.tsv'

training_set_features_local_path = os.path.join(test_data_url_prefix, 'training_set_features.tsv')
training_set_labels_local_path = os.path.join(test_data_url_prefix, 'training_set_labels.tsv')

# Path(training_set_features_local_path).write_bytes(requests.get(training_set_features_url).content)
# Path(training_set_labels_local_path).write_bytes(requests.get(training_set_labels_url).content)

#Uploading the data to GCS where it can be read by the trainer
# training_set_features_gcs_path = os.path.join(input_data_gcs_dir, 'training_set_features.tsv')
# training_set_labels_gcs_path = os.path.join(input_data_gcs_dir, 'training_set_labels.tsv')

# gfile.Copy(training_set_features_local_path, training_set_features_gcs_path)
# gfile.Copy(training_set_labels_local_path, training_set_labels_gcs_path)

# output_model_uri_template = os.path.join(output_data_gcs_dir, kfp.dsl.EXECUTION_ID_PLACEHOLDER, 'output_model_uri', 'data')
# output_model_local_template = component_url_prefix + 'tests/output/trained'

# xor_model_config = requests.get('https://raw.githubusercontent.com/kubeflow/pipelines/master/components/sample/keras/train_classifier/tests/testdata/' + 'model_config.json').content

xor_model_config = Path('./tests/testdata').joinpath('model_config.json').read_text()
# print('xor_model_config: ', type(xor_model_config), xor_model_config)


#Load the component
train_op = kfp.components.load_component_from_file('./component.yaml')
keras_convert_hdf5_model_to_tf_saved_model_op = kfp.components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/51e49282d9511e4b72736c12dc66e37486849c6e/components/_converters/KerasModelHdf5/to_TensorflowSavedModel/component.yaml')

#Use the component as part of the pipeline
@kfp.dsl.pipeline(name='Test keras/train_classifier', description='Pipeline to test keras/train_classifier component')
def pipeline_to_test_keras_train_classifier():
    train_task = train_op(
        training_set_features_path=training_set_features_local_path,
        training_set_labels_path=training_set_labels_local_path,
        model_config=xor_model_config,
        number_of_classes=2,
        number_of_epochs=10,
        batch_size=32,
    ).add_volume(k8s_client.V1Volume(name='data-processing',
                                     host_path=k8s_client.V1HostPathVolumeSource(path='/home/docker/data_processing'))) \
    .add_volume_mount(k8s_client.V1VolumeMount(mount_path='/data_processing',
                                               name='data-processing'))

    keras_model_in_tf_format = keras_convert_hdf5_model_to_tf_saved_model_op(
        model=train_task.outputs['output_model_uri'],
    ).output
    #Use train_task.outputs['output_model_uri'] to obtain the reference to the trained model URI that can be a passed to other pipeline tasks (e.g. for prediction or analysis)


# If you run this command on a Jupyter notebook running on Kubeflow,
# you can exclude the host parameter.
# client = kfp.Client()
client = kfp.Client(host='http://localhost:8080/pipeline')

# Compile, upload, and submit this pipeline for execution.
client.create_run_from_pipeline_func(pipeline_to_test_keras_train_classifier, arguments={},
    mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE)