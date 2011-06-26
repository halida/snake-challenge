class AddMapToReplays < ActiveRecord::Migration
  def self.up
    add_column :replays, :map, :string
  end

  def self.down
    remove_column :replays, :map, :string
  end
end
