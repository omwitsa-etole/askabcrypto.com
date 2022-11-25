from login.app import app, get_currencies


class Run:
    def __init__(self, app):
          self = app
          self.run(host="0.0.0.0", debug=True)
          
if __name__ == "__main__":
    Run(app)
    #get_currencies()
    #arr("descending")
    