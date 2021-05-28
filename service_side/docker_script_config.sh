docker run -t --rm -p 8501:8501 -v "${PWD}/:/" emacski/tensorflow-serving --model_config_file=/models.config
