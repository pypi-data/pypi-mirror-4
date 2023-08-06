# coding=UTF-8
'''Copyright [2012] [Ricardo García Fernández] [ricarodgarfe@gmail.com]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

'''
from scraper.primaverasound.schedule import Schedule
import json

class RetrieveSchedule:
    '''RetrieveSchedule class to retrieve Primavera Sound 2013 Schedule.

    Created on 22/03/2013

    @author: Ricardo García Fernández
    @mail: ricardogarfe@gmail.com
    
    '''
    
    def __init__(self):
        '''Init method
        '''

        primaveraSoundSchedule = Schedule()

        # Print results.
        schedule_result = json.dumps(primaveraSoundSchedule.horarios, sort_keys=True, indent=4)
        print schedule_result

def main():
    '''Main method to initialize project.
    '''

    RetrieveSchedule()

if __name__ == '__main__':
    main()     

