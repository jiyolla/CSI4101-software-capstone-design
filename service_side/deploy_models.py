import sys
import os
# import tensorflow as tf

sys.path.append(os.path.join(sys.path[0], '..'))
from common import available_models


def main():
    with open('models.config', 'w') as f:
        f.write('model_config_list {\n')
        for model in available_models.lst:
            #print(f'Loading {model}...')
            #loaded_model = eval(f'tf.keras.applications.{model}')
            #tf.saved_model.save(loaded_model(), f'./models/{model}/1')
            #print(f'{model} loaded.')
            f.write('  config {\n')
            f.write(f'    name: \'{model}\'\n')
            f.write(f'    base_path: \'/service/models/{model}/\'\n')
            f.write('    model_platform: \'tensorflow\'\n')
            f.write('  }\n')
        f.write('}')


if __name__ == '__main__':
    main()
