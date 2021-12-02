import kfp

client = kfp.Client("http://localhost:8080/pipeline")

run_result = client.run_pipeline(
    pipeline_id="923876fd-50b1-4291-9cfb-84d7fb1cfee0",
    experiment_id="57e17ee9-fc01-403b-a29f-33861df6058f",
    job_name="Example pipeline"
)
