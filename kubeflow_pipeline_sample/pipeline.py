import kfp
import kfp.components as comp
from kfp.v2.dsl import component
from kubernetes import client as k8s_client
from kfp.v2.dsl import (
    Input,
    Output,
    Artifact,
    Dataset,
)

create_step_get_lines = comp.load_component_from_file('./component.yaml')

# create_step_get_lines is a "factory function" that accepts the arguments
# for the component's inputs and output paths and returns a pipeline step
# (ContainerOp instance).
#
# To inspect the get_lines_op function in Jupyter Notebook, enter
# "get_lines_op(" in a cell and press Shift+Tab.
# You can also get help by entering `help(get_lines_op)`, `get_lines_op?`,
# or `get_lines_op??`.

@component
def print_op(input_txt: Input[Artifact]):
    with open(input_txt.path, 'r') as fr:
        for line in fr.readlines():
            print(line.strip())

# Define your pipeline
@kfp.dsl.pipeline(
    name="example-pipeline",
)
def my_pipeline():
    get_lines_step = create_step_get_lines(
        # Input name "Input 1" is converted to pythonic parameter name "input_1"
        input_1='/data_processing/input.txt',
        parameter_1='5',
        ).add_volume(k8s_client.V1Volume(name='data-processing', host_path=k8s_client.V1HostPathVolumeSource(path='/home/docker/data_processing'))) \
                        .add_volume_mount(k8s_client.V1VolumeMount(
                                        mount_path='/data_processing',
                                        name='data-processing'))

    print('write output at: ', get_lines_step.outputs, type(get_lines_step.outputs['output_1']))
    check_output_step = print_op(get_lines_step.outputs['output_1'])


# def my_pipeline():
#     get_lines_step = create_step_get_lines(
#         # Input name "Input 1" is converted to pythonic parameter name "input_1"
#         input_1='one\ntwo\nthree\nfour\nfive\nsix\nseven\neight\nnine\nten',
#         parameter_1='5',
#     )

# If you run this command on a Jupyter notebook running on Kubeflow,
# you can exclude the host parameter.
# client = kfp.Client()
client = kfp.Client(host='http://localhost:8080/pipeline')

# Compile, upload, and submit this pipeline for execution.
client.create_run_from_pipeline_func(my_pipeline, arguments={},
    mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE)
