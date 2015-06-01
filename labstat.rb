#!/usr/bin/env ruby 

#Temperature: 17.9°C 64.3°F
#Lights: likely on (average reading 8834.2, sdev 158.9)
#Power:
#        power1: 10.0W
#        power2: 118.9W
#        power3: unavailable
#        power4: 252.0W
#Total power: 380.9W

Dir.chdir("/home/jsommers/bin")

if File.exist?("/tmp/labstat.lock")
    puts ("labstat process already running")
    exit
end
File.new("/tmp/labstat.lock", "w")

temp = `/home/jsommers/bin/labtemp.sh`
temp =~ /Temperature:\s*(.*)$/
tempstr = $1
temp =~ /(\d+\.\d).C (\d+\.\d).F/
tempcval = $1
tempfval = $2
temp = tempstr

if tempfval.to_f <= 68
  tempclass = "success"
elsif tempfval.to_f > 72
  tempclass = "danger"
else
  tempclass = "warning"
end

light = `/home/jsommers/bin/lablights.sh`
light =~ /Lights: likely (\w+) \(average reading (\d+\.\d+)/
light = $1
lightintensity = $2

if light == "on"
  lightclass = "warning"
else
  lightclass = "success"
end


power = `/home/jsommers/bin/labpower.py`
power =~ /power1: (\d+\.\d+)W/m
power1 = $1 || "?"
power =~ /power2: (\d+\.\d+)W/m
power2 = $1 || "?"
power =~ /power3: (\d+\.\d+)W/m
power3 = $1 || "?"
power =~ /power4: (\d+\.\d+)W/m
power4 = $1 || "?"
power =~ /Total power: (\d+\.\d+)W/m
totpower = $1

if totpower.to_f > 1000.0
  powerclass = "warning"
elsif totpower.to_f > 500
  powerclass = "danger"
else
  powerclass = "success"
end

lastupdate = Time.new.strftime("%Y-%m-%d %H:%M:%S")

pagetemplate = <<END
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>clab.colgate.edu</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
<body>

<div id="main" class="container">
  <div id="back" class="jumbotron">
    <h1 class="text-center">Current conditions</h1>

    <table class="table table-bordered">
      <tr class="#{tempclass}"><th>Temperature
          <td id="temp" colspan="5"> #{temp}
      <tr class="#{powerclass}"><th>Power
           <td id="power">#{totpower}W
           <td class="small">pdu1: #{power1}
           <td class="small">pdu2: #{power2}
           <td class="small">pdu3: #{power3}
           <td class="small">pdu4: #{power4}
      <tr class="#{lightclass}"><th>Lights
           <td id="lights">#{light.capitalize}
           <td class="small" colspan="4">Intensity: #{lightintensity}
    </table>
    <div>
      <img src="temp.png"/>
      <img src="power.png"/>
      <img src="light.png"/>
    </div>

    <div><h6>Last update: #{lastupdate}</h6></div>

  </div>
</div>
</body>
</html>
END

File.open("/home/jsommers/bin/index.html", "w") do |f|
  f.write(pagetemplate)
end

File.open("/home/jsommers/bin/tempdata.txt", "a") do |f|
  f.write("#{lastupdate} #{tempcval} #{tempfval} #{totpower} #{power1} #{power2} #{power3} #{power4} #{light} #{lightintensity}\n")
end

`/usr/bin/gnuplot plottemp.gp`
`cp *.png /var/www/html`
`cp index.html /var/www/html`

pimon = <<END
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>clab.colgate.edu</title>
<style>
.big {
  font-size: 18pt;
}
.med {
  font-size: 14pt;
}
</style>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css">
<body>

<div id="main" class="container">
  <div id="back" class="jumbotron">
    <h1 class="text-center">Current conditions</h1>

    <table class="table table-bordered">
      <tr class="#{tempclass}"><th class="big">Temperature
          <td id="temp" colspan="5" class="big"> #{temp}
      <tr class="#{powerclass}"><th class="big">Power
           <td id="power" class="big"> #{totpower}W
           <td class="med">pdu1: #{power1}
           <td class="med">pdu2: #{power2}
           <td class="med">pdu3: #{power3}
           <td class="med">pdu4: #{power4}
      <tr class="#{lightclass}"><th class="big">Light
          <td id="light" colspan="5" class="big"> #{light.capitalize} (#{lightintensity})
    </table>
    <div><h6>Last update: #{lastupdate}</h6></div>
  </div>
</div>
</body>
</html>
END
File.open("/home/jsommers/bin/pimon.html", "w") do |f|
  f.write(pimon)
end
`cp pimon.html /var/www/html`

File.unlink("/tmp/labstat.lock")
