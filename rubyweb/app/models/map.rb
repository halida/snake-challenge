class Map < ActiveRecord::Base
  include_root_in_json = false
  
  validates_presence_of :title
  validates_uniqueness_of :title
  
  validates :height, {
    :presence => true,
    :inclusion => { :in => 10..150 }
  } 
  validates :width, {
    :presence => true,
    :inclusion => { :in => 10..150 }
  }

  serialize :walls
  # {"walls"=>[[8, 7], [10, 7], [6, 8]], "height"=>15, "width"=>15}
end
