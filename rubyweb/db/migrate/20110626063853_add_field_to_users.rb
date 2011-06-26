class AddFieldToUsers < ActiveRecord::Migration
  def self.up
    add_column :users, :name, :string , :null => false
    add_column :users, :blog, :string
    add_column :users, :twitter, :string
    add_column :users, :bio, :string
  end

  def self.down
    remove_column :users, :name
    remove_column :users, :blog
    remove_column :users, :twitter
    remove_column :users, :bio
  end
end
