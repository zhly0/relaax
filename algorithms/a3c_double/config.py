class Config:
    def __init__(self):
        # gym's environment name
        self.env_name0 = 'PongDeterministic-v4'
        self.env_name1 = 'BreakoutDeterministic-v4'
        # 'MontezumaRevengeDeterministic-v3'

        # action size for given environment
        self.action_size0 = 6   # 6 (Pong)
        self.action_size1 = 4   # 6->4 (Breakout)

        # size of the input observation (image to pass through 2D Convolution)
        self.state_size = [84, 84, 3]   # Box(210, 160, 3) - default

        # number of threads
        self.threads_num = 8

        # local loop size for one episode
        self.LOCAL_T_MAX = 20   # 10 (Lab) | 10 (MR) | 20 (Pong)

        # learning rate
        self.entropy_beta = 1e-2

        # learning rate
        self.learning_rate = 7e-4

        # maximum global time step
        self.MAX_TIME_STEP = 10 * 10 ** 7

        self.RMSP_ALPHA = 0.99   # decay parameter for RMSProp
        self.RMSP_EPSILON = 0.1  # epsilon parameter for RMSProp

        self.GAMMA = 0.99  # discount factor for rewards

cfg = Config()