class CreateMaps < ActiveRecord::Migration
  def self.up
    create_table(:maps) do |t|
      t.integer :user_id
      t.string :title
      t.text :walls

      t.integer :height
      t.integer :width
      
      t.timestamps
    end
  end

  def self.down
    drop_table :maps
  end
end
