Rubyweb::Application.routes.draw do
  ActiveAdmin.routes(self)

  devise_for :admin_users, ActiveAdmin::Devise.config

  resources :replays

  root :to => "home#index"
  resources :room, :controller => :rooms do
    member do
      get :info
      get :map
      post :add
      post :turn
    end
  end

  resources :maps

  match '/chat/message' => 'chat#message'
  match '/chat/info' => 'chat#info'
  match '/chat' => 'chat#index'

  devise_for :users

end
