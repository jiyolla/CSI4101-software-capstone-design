docker run -t --rm -p 8501:8501 -v "/home/nano/img_clf/:/models/" emacski/tensorflow-serving --model_config_file=/models/models.config
