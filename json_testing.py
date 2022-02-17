import json

mail_test1='''
{
    "alarm": [
        {
            "service_name": "CPU Utilization",
            "message": "Host has more than 75% CPU utilization",
            "Severity" : "Warning",
            "Host" : "web-stg-001",
            "Availability_Domain": "AD1",
            "Sendby": "OCI monitoring"
        },
        {
            "service_name": "CPU Utilization",
            "message": "Host has more than 90% CPU utilization",
            "Severity" : "Critical",
            "Host" : "web-stg-001",
            "Availability_Domain": "AD1",
            "Sendby": "OCI monitoring"
        }
    ]
    
}
'''
#So the objects when loaded is becoming dictionary of lists
data = json.loads(mail_test1)
print(type(data))
#prints <class 'dict'>
print(type(data['alarm']))
#prints <class 'lil'>

for alarm_data in data['alarm']:
    print(alarm_data)

print("Removing the Sendby from Dictionary and make it object again without it")
for alarm_data in data['alarm']:
    del alarm_data['Sendby']

new_string = json.dumps(data)
print(new_string)
