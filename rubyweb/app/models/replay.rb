class Replay < ActiveRecord::Base
  scope :recent, :order => "id desc"
end
