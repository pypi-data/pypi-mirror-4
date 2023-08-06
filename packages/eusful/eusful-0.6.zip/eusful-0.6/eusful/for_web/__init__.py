import web

def get_input():
  try:
    return web.input()
  except:
    return web.input(_unicode=False)