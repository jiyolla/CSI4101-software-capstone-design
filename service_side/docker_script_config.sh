docker run -t --rm -p 8501:8501 -v "${PWD}/:/service/" emacski/tensorflow-serving --model_config_file=/service/models.config
