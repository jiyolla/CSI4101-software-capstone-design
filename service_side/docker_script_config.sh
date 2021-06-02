docker run -t --rm -p 8501:8501 -v "${PWD}/:/service/" emacski/tensorflow-serving:2.4.1-linux_arm64_armv8-a --model_config_file=/service/models.config
