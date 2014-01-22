from xml.dom import pulldom


class EventStream(object):
    def __init__(self, stream):
        self._stream = stream
    
    def __iter__(self):
        return self
    
    def next(self):
        return next(self._stream)

    def seek(self, predicate, ignore):
        if isinstance(predicate, basestring):
            desired_event = predicate
            predicate = lambda event, node: event == desired_event
        while True:
            event, node = next(self._stream)
            if predicate(event, node):
                return event, node
            elif not event in ignore:
                raise ValueError("Event {0} before desired event {1}".format(event, desired_event))


    def inner_text(self):
        text = []
        level = 1
        while level > 0:
            event, node = next(self._stream)
            if event == pulldom.START_ELEMENT:
                level += 1
            elif event == pulldom.END_ELEMENT:
                level -= 1
            elif event == pulldom.CHARACTERS:
                text.append(node.nodeValue)
        
        return "".join(text)
