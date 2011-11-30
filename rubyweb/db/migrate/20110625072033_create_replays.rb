class CreateReplays < ActiveRecord::Migration
  def self.up
    create_table :replays do |t|
      t.string :title, :null => false
      t.text :json, :null => false
      t.integer :user_id
      t.timestamps
    end
  end

  def self.down
    drop_table :replays
  end
end
