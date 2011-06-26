class Replay < ActiveRecord::Base
  scope :recent, :order => "id desc"

  before_create :auto_title

  def auto_title
    self.title = Time.now.strftime("%Y%m%d%H%M")
  end
end
