class CreateReplays < ActiveRecord::Migration
  def self.up
    create_table :replays do |t|
      t.string :title, :null => false
      t.integer :round, :null => false, :default => 0
      t.text :json, :null => false

      t.timestamps
    end
  end

  def self.down
    drop_table :replays
  end
end
