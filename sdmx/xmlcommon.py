def inner_text(element):
  return (element.text or "") + "".join(map(inner_text, element)) + (element.tail or "")
