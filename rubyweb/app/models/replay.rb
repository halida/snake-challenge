class Replay < ActiveRecord::Base
  scope :recent, :order => "id desc"

  belongs_to :user

end
