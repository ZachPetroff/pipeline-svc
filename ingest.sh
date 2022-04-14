#!/bin/bash
sudo apt-get install wget
# remove previous csv file
rm *.csv
# download new data 
echo Enter Data URL
read data 
wget $data -O data.csv 
