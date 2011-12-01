files = `find ../srcs/map |grep yml`.split
Map.delete_all
for file in files
  data = YAML.load File.open(file).read()
  puts data['name']
  Map.create! title: data['name'], width: data['width'], height: data['height'], data: JSON.dump(data)
end
  
