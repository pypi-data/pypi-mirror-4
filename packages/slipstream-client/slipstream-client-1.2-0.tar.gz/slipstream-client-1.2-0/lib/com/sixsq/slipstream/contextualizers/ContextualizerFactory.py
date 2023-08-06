from com.sixsq.slipstream.contextualizers.dummy.LocalContextualizer import LocalContextualizer

class ContextualizerFactory(object):

    @staticmethod
    def createContextualizer():
        return LocalContextualizer()

    @staticmethod
    def getContextAsDict():
        contextualizer = ContextualizerFactory.createContextualizer()
        return contextualizer.getContextAsDict()

