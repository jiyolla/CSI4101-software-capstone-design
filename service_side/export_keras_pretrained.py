import tensorflow as tf

pretrained_model = tf.keras.applications.Xception()
tf.saved_model.save(pretrained_model, './models/Xception/1')

pretrained_model = tf.keras.applications.MobileNetV2()
tf.saved_model.save(pretrained_model, './models/MobileNetV2/1')

pretrained_model = tf.keras.applications.DenseNet121()
tf.saved_model.save(pretrained_model, './DenseNet121/1')

pretrained_model = tf.keras.applications.DenseNet169()
tf.saved_model.save(pretrained_model, './DenseNet169/1')

pretrained_model = tf.keras.applications.DenseNet201()
tf.saved_model.save(pretrained_model, './DenseNet201/1')

pretrained_model = tf.keras.applications.NASNetMobile()
tf.saved_model.save(pretrained_model, './NASNetMobile/1')
