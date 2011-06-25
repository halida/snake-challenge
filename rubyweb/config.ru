require 'rubygems'
require 'sinatra'

set :run, false
set :environment, :production

disable :reload

load 'server.rb'

run Sinatra::Application
