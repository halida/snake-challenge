class CreateMaps < ActiveRecord::Migration
  def change
    create_table :maps do |t|
      t.integer :user
      t.string :title
      t.text :data
      t.integer :height
      t.integer :width

      t.timestamps
    end
  end
end
