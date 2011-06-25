express = require "express"
app = express.createServer()

app.register('.haml', require('hamljs'))

app.get '/', (req,res) ->
  # res.send('Hello World')
  res.render "index.haml"

app.listen(3000)