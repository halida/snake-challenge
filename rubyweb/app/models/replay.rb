class Replay < ActiveRecord::Base
  scope :recent, :order => "id desc"

  belongs_to :user

  before_create :auto_title

  def auto_title
    self.title = Time.now.strftime("%Y/%m/%d %H:%M:%S")
  end
end
