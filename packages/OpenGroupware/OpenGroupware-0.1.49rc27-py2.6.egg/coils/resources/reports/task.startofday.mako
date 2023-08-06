  <body>
  <table style="border:1px solid #98bf21;border-collapse:collapse;">
    %if report['start']:
        <tr>
          <td style="font-size:2em;background: blue; color: white">You have ${len(report['start'])} tasks starting today.</td>
         </tr>
      <tr><td>
         <table width=100%>
           <tr><th style="border:1px solid #98bf21;padding:3px 7px 2px 7px;font-size:1em;">Id</th>
               <th style="border:1px solid #98bf21;padding:3px 7px 2px 7px;font-size:1em;">Name</th>
               <th style="border:1px solid #98bf21;padding:3px 7px 2px 7px;font-size:1em;">Start</th>
               <th style="border:1px solid #98bf21;padding:3px 7px 2px 7px;font-size:1em;">End</th>
               <th style="border:1px solid #98bf21;padding:3px 7px 2px 7px;font-size:1em;">Status</th>
               <th style="border:1px solid #98bf21;padding:3px 7px 2px 7px;font-size:1em;">Priority</th>
               <th style="border:1px solid #98bf21;padding:3px 7px 2px 7px;font-size:1em;">Owner</th></tr>
         %for i,task in enumerate(report['start'][:10]):
           <tr><td align=center><a href="https://iv5.mormail.com/Tasks/view/${str(task.object_id)}">${str(task.object_id)}</a></td>
               <td>${task.name}</td>
               <td align=center>${task.start.strftime('%Y-%m-%d')}</td>
               <td align=center>${task.end.strftime('%Y-%m-%d')}</td>
               <td align=center>${get_task_status(task.state).strip()}</td>
               <td align=center>${get_task_priority(task.priority)}</td>
               %if task.owner:
                  <td>${task.owner.get_display_name()}</td>
               %else:
                  <td>unknown</td>
               %endif
           </tr>
         %endfor
         %if len(report['start'])> 10:
           <tr><td colspan=7><a href="https://iv5.mormail.com/Tasks/">More...</a></td></tr>
         %endif
        </table> 
      </td></tr>
    %endif
       
   %if report['end']:
        <tr><td style="font-size:2em;background: #CD2626;color:#FFCC11">You have ${len(report['end'])} tasks due today.</td></tr>
     <tr><td>
         <table width=100%>
           <tr><th style="border:1px solid #98bf21;padding-top:5px;padding-bottom:4px;font-size:1em;background-color:#A7C942;
color:#ffffff;">Id</th>
               <th style="border:1px solid #98bf21;padding-top:5px;padding-bottom:4px;font-size:1em;background-color:#A7C942;
color:#ffffff;">Name</th>
               <th style="border:1px solid #98bf21;padding-top:5px;padding-bottom:4px;font-size:1em;background-color:#A7C942;
color:#ffffff;">Start</th>
               <th style="border:1px solid #98bf21;padding-top:5px;padding-bottom:4px;font-size:1em;background-color:#A7C942;
color:#ffffff;">End</th>
               <th style="border:1px solid #98bf21;padding-top:5px;padding-bottom:4px;;font-size:1em;background-color:#A7C942;
color:#ffffff;">Status</th>
               <th style="border:1px solid #98bf21;padding-top:5px;padding-bottom:4px;font-size:1em;background-color:#A7C942;
color:#ffffff;">Priority</th>
               <th style="border:1px solid #98bf21;padding-top:5px;padding-bottom:4px;font-size:1em;background-color:#A7C942;
color:#ffffff;">Owner</th></tr>
         %for i, task in enumerate(report['end'][:10]):
           %if i%2:
             <tr style="color:#000000;background:#FAEBD7;">
           %else:
             <tr style="color:#000000;background:#CDB38B;">
           %endif
               <td align=center><a href="https://iv5.mormail.com/Tasks/view/${str(task.object_id)}">${str(task.object_id)}</a></td>
               <td>${task.name}</td>
               <td align=center>${task.start.strftime('%Y-%m-%d')}</td>
               <td align=center>${task.end.strftime('%Y-%m-%d')}</td>
               <td align=center>${get_task_status(task.state).strip()}</td>
               <td align=center>${get_task_priority(task.priority)}</td>
               %if task.owner:
                  <td>${task.owner.get_display_name()}</td>
               %else:
                  <td>unknown</td>
               %endif    
           </tr>                          
         %endfor
         %if len(report['end'])> 10:
           <tr><td colspan=7><a href="https://iv5.mormail.com/Tasks/">More...</a></td></tr>
         %endif
        </table> </td></tr>
   %endif       
      
   %if report['overdue']:
     <tr>
       <td  style="font-size:2em;background: #EE0000; color: yellow">You have ${len(report['overdue'])} overdue tasks.</td>
      </tr>
     <tr>
       <td>
         <table width=100%>
           <tr><th style="background:#FF3333;border:1px solid #FF0000;padding-top:5px;padding-bottom:4px;font-size:1em; color: white">Id</th>
               <th style="background:#FF3333;border:1px solid #FF0000;padding-top:5px;padding-bottom:4px;font-size:1em; color: white">Name</th>
               <th style="background:#FF3333;border:1px solid #FF0000;padding-top:5px;padding-bottom:4px;font-size:1em; color: white">End</th>
               <th style="background:#FF3333;border:1px solid #FF0000;padding-top:5px;padding-bottom:4px;font-size:1em; color: white">Status</th>
               <th style="background:#FF3333;border:1px solid #FF0000;padding-top:5px;padding-bottom:4px;font-size:1em; color: white">Priority</th>
               <th style="background:#FF3333;border:1px solid #FF0000;padding-top:5px;padding-bottom:4px;font-size:1em; color: white">Owner</th></tr>
         %for i, task in enumerate(report['overdue'][:10]):
           %if i%2 == 0:
             <tr style="background:#FFC1C1;border:1px solid #FF0000;color: black;">
           %else:
             <tr style="background:##C65D57;border:1px solid #FF0000;color: black;">
           %endif
               <td><a href="https://iv5.mormail.com/Tasks/view/${str(task.object_id)}">${str(task.object_id)}</a></td>
               <td>${task.name}</td>
               <td>${task.end.strftime('%Y-%m-%d')}</td>
               <td>${get_task_status(task.state).strip()}</td>
               <td>${get_task_priority(task.priority)}</td>
               %if task.owner:
                  <td>${task.owner.get_display_name()}</td>
               %else:
                  <td>unknown</td>
               %endif  
           </tr>
         %endfor
         %if len(report['overdue'])> 10:
           <tr><td colspan=7><a href="https://iv5.mormail.com/Tasks/">More...</a></td></tr>
         %endif
         </table>     
       </td>
     </tr>
   %else:
     <tr>
       <td style="background:#FFC469;border:1px solid #8C7853;color: black;">You have no overdue tasks.</td>
      </tr>
   %endif    
              
   <tr>
     <td>
       <table width=100%>
       <tr style="background:#8B7E66;border:1px solid #8C7853;color: white;">
         <th colspan=4 >Your task lists.</th>
        </tr>
       <tr style="background:#8C7853;border:1px solid #8C7853;color: white;">
         <td>Status</td>
         <th>To-Do</th>
         <th>Delegated</th>
         <th>Project</th>
        </tr>
       <tr style="background:#FEF0DB;border:1px solid #8C7853;color: black;">
           <td>Created</td>
           <td align="center">${len(report['todo']['00_created'])}</td>
           <td align="center">${len(report['dlgt']['00_created'])}</td>
           <td align="center">${len(report['proj']['00_created'])}</td></tr>
       <tr style="background:#FFDEAD;border:1px solid #8C7853;color: black;">
           <td>Rejected</td>
           <td align="center">${len(report['todo']['02_rejected'])}</td>
           <td align="center">${len(report['dlgt']['02_rejected'])}</td>
           <td align="center">${len(report['proj']['02_rejected'])}</td></tr>
       <tr style="background:#FFEBCD;border:1px solid #8C7853;color: black;">
           <td>Processing</td>
           <td align="center">${len(report['todo']['20_processing'])}</td>
           <td align="center">${len(report['dlgt']['20_processing'])}</td>
           <td align="center">${len(report['proj']['20_processing'])}</td></tr>
       <tr style="background:#CDBA96;border:1px solid #8C7853;color: black;">
           <td>Done</td>
           <td align="center">${len(report['todo']['25_done'])}</td>
           <td align="center">${len(report['dlgt']['25_done'])}</td>
           <td align="center">${len(report['proj']['25_done'])}</td>
           </tr>
       </table>                     
     </td>
    </tr>
   <tr>
     <td>
       <table width=100%>
         <tr style="background:#8B7E66;border:1px solid #8C7853;color: white;">
            <th colspan = 4>Yesterday's Activity</th>
          </tr>
       <tr style="background:#8C7853;border:1px solid #8C7853;color: white;">
         <th>Action</th>
         <th>User</th>
         <th>On Delegated Tasks</th>
         <th>On Project Tasks</th>
        </tr>
       <tr style="background:#FEF0DB;border:1px solid #8C7853;color: black;">
         <td>Created</td>
         <td align="center">${report['eod']['user']['00_created']}</td>
         <td align="center">${report['eod']['dlgt']['00_created']}</td>
         <td align="center">${report['eod']['proj']['00_created']}</td>
        </tr>
       <tr style="background:#FFDEAD;border:1px solid #8C7853;color: black;">
         <td>Rejected</td>
         <td align="center">${report['eod']['user']['02_rejected']}</td>
         <td align="center">${report['eod']['dlgt']['02_rejected']}</td>
         <td align="center">${report['eod']['proj']['02_rejected']}</td>
        </tr>
       <tr style="background:#FFEBCD;border:1px solid #8C7853;color: black;">
         <td>Accepted</td>
         <td align="center">${report['eod']['user']['05_accepted']}</td>
         <td align="center">${report['eod']['dlgt']['05_accepted']}</td>
         <td align="center">${report['eod']['proj']['05_accepted']}</td>
        </tr>
       <tr style="background:#FDF5E6;border:1px solid #8C7853;color: black;">
         <td>Commented</td>
         <td align="center">${report['eod']['user']['10_commented']}</td>
         <td align="center">${report['eod']['dlgt']['10_commented']}</td>
         <td align="center">${report['eod']['proj']['10_commented']}</td>
        </tr>          
       <tr style="background:#CDBA96;border:1px solid #8C7853;color: black;">
         <td>Completed</td>
         <td align="center">${report['eod']['user']['25_done']}</td>
         <td align="center">${report['eod']['dlgt']['25_done']}</td>
         <td align="center">${report['eod']['proj']['25_done']}</td>
        </tr>
       <tr style="background:#D5B77A;border:1px solid #8C7853;color: black;">
         <td>Archived</td>
         <td align="center">${report['eod']['user']['30_archived']}</td>
         <td align="center">${report['eod']['dlgt']['30_archived']}</td>
         <td align="center">${report['eod']['proj']['30_archived']}</td>
        </tr>
      </table> 
     </td>
    </tr>  
  </table>
  </body>
       
      <%def name="get_task_status(state)">
        %if state == '00_created': 
           created
        %elif state == '02_rejected':
           rejected
        %elif state == '20_processing':
           processing
        %elif state == '25_done':
           done 
        %elif state == '30_archived':
           done                      
        %else:
           unknown
        %endif
      </%def>
      
      <%def name="get_task_priority(priority)">
        %if priority == 1: 
           very low
        %elif priority == 2:
           low
        %elif priority == 3:
           average
        %elif priority == 4:
           high 
        %elif priority == 5:
           very high                      
        %else:
           unknown
        %endif
      </%def>
