import tensorflow as tf
from tensorflow.python.ops import init_ops
import numpy as np

from relaax.common.algorithms.lib import utils
from relaax.common.algorithms import subgraph


class DefaultInitializer(object):
    INIT = {
        np.float32: (tf.float32, init_ops.glorot_uniform_initializer)
    }

    def __call__(self, dtype=np.float32, shape=None):
        tf_dtype, initializer = self.INIT[dtype]
        return initializer(dtype=tf_dtype)(shape=shape, dtype=tf_dtype)


class ZeroInitializer(object):
    def __call__(self, dtype=np.float32, shape=None):
        return np.zeros(shape=shape, dtype=dtype)


class OneInitializer(object):
    def __call__(self, dtype=np.float32, shape=None):
        return np.ones(shape=shape, dtype=dtype)


class RandomUniformInitializer(object):
    DTYPE = {
        np.float: tf.float64,
        np.float64: tf.float64,
        np.float32: tf.float32,
    }

    def __init__(self, minval=0, maxval=1):
        self.minval = minval
        self.maxval = maxval

    def __call__(self, dtype=np.float32, shape=None):
        return tf.random_uniform(
            shape,
            dtype=self.DTYPE[dtype],
            minval=self.minval,
            maxval=self.maxval
        )


class XavierInitializer(object):
    DTYPE = {
        np.float: tf.float64,
        np.float64: tf.float64,
        np.float32: tf.float32,
    }

    def __call__(self, dtype=np.float32, shape=None):
        return tf.contrib.layers.xavier_initializer()(
            dtype=self.DTYPE[dtype],
            shape=shape
        )


class AdamOptimizer(subgraph.Subgraph):
    def build_graph(self, learning_rate=0.001):
        return tf.train.AdamOptimizer(learning_rate=learning_rate)


class RMSPropOptimizer(subgraph.Subgraph):
    def build_graph(self, learning_rate, decay, momentum, epsilon):
        return tf.train.RMSPropOptimizer(
            learning_rate=learning_rate.node,
            decay=decay,
            momentum=momentum,
            epsilon=epsilon
        )


class ApplyGradients(subgraph.Subgraph):
    def build_graph(self, optimizer, weights, gradients):
        return optimizer.node.apply_gradients(utils.Utils.izip(gradients.node, weights.node))


class Gradients(subgraph.Subgraph):
    def build_graph(self, loss, variables):
        return utils.Utils.reconstruct(
            tf.gradients(loss.node, list(utils.Utils.flatten(variables.node))),
            variables.node
        )


class Reshape(subgraph.Subgraph):
    def build_graph(self, x, shape):
        return tf.reshape(x.node, shape)


class Flatten(subgraph.Subgraph):
    def build_graph(self, x):
        return Reshape(x, (-1, )).node


class Convolution(subgraph.Subgraph):
    def build_graph(self, x, wb, stride):
        return tf.nn.conv2d(x.node, wb.W, strides=[1, stride, stride, 1], padding="VALID") + wb.b


class Relu(subgraph.Subgraph):
    def build_graph(self, x):
        return tf.nn.relu(x.node)


class Reshape(subgraph.Subgraph):
    def build_graph(self, x, shape):
        return tf.reshape(x.node, shape)


class Softmax(subgraph.Subgraph):
    def build_graph(self, x):
        return tf.nn.softmax(x.node)


class List(subgraph.Subgraph):
    def build_graph(self, items):
        self.items = list(items)
        return map(lambda i: i.node, self.items)


class Assign(subgraph.Subgraph):
    def build_graph(self, variables, values):
        return [
            tf.assign(variable, value)
            for variable, value in utils.Utils.izip(
                variables.node,
                values.node
            )
        ]


class Increment(subgraph.Subgraph):
    def build_graph(self, variable, increment):
        return tf.assign_add(variable.node, increment.node)


class Placeholder(subgraph.Subgraph):
    """Placeholder of given shape."""

    DTYPE = {
        np.int32: tf.int32,
        np.int64: tf.int64,
        np.float32: tf.float32
    }

    def build_graph(self, dtype, shape=None):
        """Assemble one placeholder.

        Args:
            shape: placehoder shape
            dtype: placeholder data type

        Returns:
            placeholder of given shape and data type
        """

        return tf.placeholder(self.DTYPE[dtype], shape=shape)


class Placeholders(subgraph.Subgraph):
    def build_graph(self, variables):
        print repr(variables)
        return utils.Utils.map(
            variables.node,
            lambda v: tf.placeholder(shape=v.get_shape(), dtype=v.dtype)
        )


class GlobalStep(subgraph.Subgraph):
    def build_graph(self, increment):
        self.n = Variable(0, dtype=np.int64)
        self.increment = Increment(self.n, increment)


class Variable(subgraph.Subgraph):
    DTYPE = {
        None: None,
        np.int64: tf.int64
    }

    def build_graph(self, initial_value, dtype=None):
        return tf.Variable(initial_value, dtype=self.DTYPE[dtype])


class Variables(subgraph.Subgraph):
    def build_graph(self, *variables):
        return [variable.node for variable in variables]

    def assign(self, values):
        return TfNode([
            tf.assign(variable, value)
            for variable, value in utils.Utils.izip(
                self.node,
                values.node
            )
        ])



class Wb(subgraph.Subgraph):
    def build_graph(self, dtype, shape):
        d = 1.0 / np.sqrt(np.prod(shape[:-1]))
        initializer = RandomUniformInitializer(minval=-d, maxval=d)
        self.W = Variable(initializer(dtype, shape     )).node
        self.b = Variable(initializer(dtype, shape[-1:])).node
        return self.W, self.b


class ApplyWb(subgraph.Subgraph):
    def build_graph(self, x, wb):
        return tf.matmul(x.node, wb.W) + wb.b


class FullyConnected(subgraph.Subgraph):
    """Builds fully connected neural network."""

    def build_graph(self, state, weights):
        last = state
        for wb in weights.items:
            last = Relu(ApplyWb(last, wb))
        return last.node


class PolicyLoss(subgraph.Subgraph):
    def build_graph(self, action, action_size, network, discounted_reward):
        # making actions that gave good advantage (reward over time) more likely,
        # and actions that didn't less likely.

        log_like_op = tf.log(tf.reduce_sum(
            tf.one_hot(action.node, action_size) * network.node,
            axis=[1]
        ))
        return -tf.reduce_sum(log_like_op * discounted_reward.node)


class Initialize(subgraph.Subgraph):
    def build_graph(self):
        return tf.global_variables_initializer()


class TfNode(subgraph.Subgraph):
    def build_graph(self, tf_tensor):
        return tf_tensor