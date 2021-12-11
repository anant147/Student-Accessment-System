import psycopg2
from flask import Flask, render_template, request,redirect
# from flask_wtf import Form
# from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField,SelectField
# from wtforms import validators, ValidationError

app = Flask(__name__)



# db = "proj"
# ur = "postgres"
# ht = "localhost"
# pword = "12345"

# con = psycopg2.connect(dbname=db,user=ur,host=ht,password=pword)                                                                     


# Server db connection

db = "group_4"
ur = "group_4"
ht = "10.17.50.134"
pword = "117-958-344"

print ("Connected to DB:","DBName-",db,"Host-",ht,"\n")
con = psycopg2.connect(dbname=db,user=ur,host=ht,password=pword)                                                                     

cur = con.cursor()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/registerpage')
def registerpage():
	return render_template('register.html')

@app.route('/registerform',methods=['POST', 'GET'])
def registerform():
	if request.method =='POST':
		result=request.form
		name=result['name']
		gender=result['gender']
		if gender=='male':
			gender='M'
		else:
		    gender='F'
		region=result['region']    
		email=result['email']
		password=result['password']
		tupl1=(name,gender,region)
		#tupl2=(email,password,'Student')
		print('tupl1 - ',tupl1)
		#print('tupl2 - ',tupl2)
		query1="insert into student_main_info (name,gender,region) values (%s,%s,%s)"
		cur.execute(query1,tupl1)
		# con.commit()
		query2="select max(id_student) from student_main_info"
		cur.execute(query2)
		items=cur.fetchall()
		person_id=items[0][0]
		tupl2=(email,password,'Student',person_id)
		query3="insert into login_info (login_id,password,login_role,person_id) values (%s,%s,%s,%s)"
		cur.execute(query3,tupl2)
		con.commit()
		return render_template('mainStudent.html',studentid=person_id)    	


 # login_id,password,login_role,person_id 


@app.route('/loginpage')
def loginpage():
	return render_template('login.html')

@app.route('/loginform',methods=['POST', 'GET'])
def loginform():
	if request.method =='POST':
		result=request.form
		email=result['email']
		password=result['password']
		query1="select * from login_info where login_id=%s"
		cur.execute(query1,(email,))
		items=cur.fetchall()
		pword=items[0][1]
		loginrole=items[0][2]
		person_id=items[0][3]
		if password != pword:
			return redirect('/loginpage')
		else:
		    if loginrole == 'Student':
		    	return render_template('mainStudent.html',studentid=person_id)
		    elif loginrole =='Teacher':
		        return render_template('mainTeacher.html',teacherid=person_id)
		    elif loginrole == 'Admin':
		        return render_template('mainAdmin.html',adminid=person_id)        


 ######################################## Student ###########################################################################



@app.route('/get_student_basic_info',methods=['POST', 'GET'])
def get_student_basic_info():
	id_student=request.get_json()["student_id"]
	

	if id_student == "":
		print('yes')
	else:
	    print('no')	
	query1="select * from student_main_info where id_student = %s"
	cur.execute(query1,(id_student,))
	items=cur.fetchall()
	stud=items[0]
	query2="select * from subject_name,(select code_module from subject_name except select distinct(code_module) from studentinfo where id_student = %s ) as t1 where subject_name.code_module=t1.code_module"
	cur.execute(query2,(id_student,))
	resub=cur.fetchall()
	print('resub - ',resub)
	print('id_student - ',id_student)
	print('data returnrd - ',stud)
	return {"data": stud}

	###############      by anant start ####################



@app.route('/show_student_profile')
def show_student_profile():
	studentid = (dict(request.args))['student_id']
	query="select * from student_main_info where id_student= %s"
	cur.execute(query,(studentid,))
	items=cur.fetchall()
	result=items[0]
	print('result - ',result)
	return render_template('studentprofile.html',studentid=studentid,output=result)


@app.route('/list_student_assessment')
def list_student_assessment():
	studentid = (dict(request.args))['student_id']
	query = "select stud_asthaptype_agsco.code_module,stud_asthaptype_agsco.code_presentation,teacher_subject.subject_name,teacher_subject.teacher_name,stud_asthaptype_agsco.id_student,stud_asthaptype_agsco.student_name,stud_asthaptype_agsco.assessment_type,stud_asthaptype_agsco.agrweight,stud_asthaptype_agsco.agrscore from stud_asthaptype_agsco,teacher_subject where stud_asthaptype_agsco.id_student=%s  and teacher_subject.code_module= stud_asthaptype_agsco.code_module and teacher_subject.code_presentation=stud_asthaptype_agsco.code_presentation"
	cur.execute(query,(studentid,))
	result=cur.fetchall()
	print(result)
	return render_template('studentassessment.html',studentid=studentid,output=result)


# @app.route('/list_student_assessment')
# def list_student_assessment():

@app.route('/list_student_courses')
def list_student_courses():
	studentid = (dict(request.args))['student_id']
	query="select t2.code_module,t2.code_presentation,t2.subject_name,teacher.name,t2.id_teacher,t2.final_result from teacher,(select teacher_course.id_teacher,teacher_course.subject_name,t1.code_module,t1.code_presentation,t1.final_result from teacher_course,(select code_module,code_presentation,final_result from studentinfo where id_student=2137171) as t1 where t1.code_module = teacher_course.code_module and t1.code_presentation =  teacher_course.code_presentation) as t2 where t2.id_teacher=teacher.id_teacher order by t2.code_presentation,t2.code_module"
	cur.execute(query,(studentid),)
	result=cur.fetchall()
	return render_template('studcourses.html',studentid=studentid,output=result)


@app.route('/list_recommedned_course')
def list_recommedned_course():
	studentid = (dict(request.args))['student_id']
	query="select t3.code_module,t3.subject_name,teacher.name,teacher.id_teacher from teacher,(select teacher_course.id_teacher,t2.code_module,t2.subject_name from teacher_course,(select subject_name.code_module,subject_name.subject_name from subject_name,(select code_module from subject_name except select distinct(code_module) from studentinfo where id_student = %s  ) as t1 where subject_name.code_module=t1.code_module) as t2 where teacher_course.code_module=t2.code_module group by teacher_course.id_teacher,t2.code_module,t2.subject_name ) as t3 where teacher.id_teacher=t3.id_teacher order by t3.code_module"
	cur.execute(query,(studentid,))
	result=cur.fetchall()
	return render_template('studrecommendcourse.html',studentid=studentid,output=result)		


@app.route('/student_course_info')
def student_course_info():
	studentid = (dict(request.args))['studentid']
	code_module = (dict(request.args))['code_module']
	code_presentation = (dict(request.args))['code_presentation']
	print(studentid,code_module,code_presentation)
	query1="select * from course_total_student,course_commencement_date where course_total_student.code_presentation =course_commencement_date.code_presentation and course_total_student.code_module=%s and course_total_student.code_presentation=%s "
	tupl1=(code_module,code_presentation)
	cur.execute(query1,tupl1)
	tcount1=cur.fetchall()
	tcount=tcount1[0]
	# print(tcount)
	query2="select * from  course_final_result where code_module=%s and code_presentation=%s"
	cur.execute(query2,tupl1)
	resultcount=cur.fetchall()
	print(resultcount)
	query3="select * from tr_sub_dat_stid_stnm where code_module=%s and code_presentation=%s order by final_result limit 2"
	cur.execute(query3,tupl1)
	studlist=cur.fetchall()
	# print(studlist)
	query4="select getDurationOfCourseModule(%s,%s)"
	tupl4=(code_module,code_presentation)
	cur.execute(query4,tupl4)
	duration=cur.fetchall()
	duration=duration[0][0]
	print('duration -',duration)
	query5="select getNoOfAssessmentInCourse(%s,%s)"
	cur.execute(query5,tupl4)
	noOfAmt=cur.fetchall()
	cnt=0
	noOfAmt1=[]
	print(noOfAmt)
	for row in noOfAmt:
		for j in row:
			l=j[1:-1]
			val=l.split(",")
			noOfAmt1.append(val)
	msgNoOfAmt='Number of Assessments in this course'
	query6=" select finalscore,grade,stud_grade.final_result from stud_fs_result,stud_grade where stud_fs_result.id_student=%s and stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s and  stud_fs_result.code_module = stud_grade.code_module and stud_fs_result.code_presentation = stud_grade.code_presentation and stud_fs_result.id_student = stud_grade.id_student"
	tupl6=(studentid,code_module,code_presentation)
	cur.execute(query6,tupl6)
	print('tupl6 - ',tupl6)
	resmetric=cur.fetchall()
	resmetric1=resmetric[0]
	print('resmetric - ',resmetric1)
	query7="select \'Average\' as Criteria,(avg(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s union select \'Minimum\' as Criteria,(min(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s union select \'Maximum\' as Criteria,(max(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s"
	tupl7=(code_module,code_presentation,code_module,code_presentation,code_module,code_presentation)
	cur.execute(query7,tupl7)
	summary=cur.fetchall()
	sumheader=["Criteria","Score"]
	sumsg="Summary of Performance of Students for "+code_module+" "+code_presentation
	query8="select stud_asthaptype_agsco.assessment_type,(stud_asthaptype_agsco.agrweight::NUMERIC) from stud_asthaptype_agsco where stud_asthaptype_agsco.code_module=%s and stud_asthaptype_agsco.code_presentation=%s GROUP BY stud_asthaptype_agsco.assessment_type,stud_asthaptype_agsco.agrweight"
	cur.execute(query8,tupl1)
	assweight=cur.fetchall()
	asswgtmsg="Weight of various assessment type for  "+code_module+" "+code_presentation
	return render_template('student_course_info.html',studentid=studentid,tcount=tcount,resultcount=resultcount,studlist=studlist,
		duration=duration,noOfAmt=noOfAmt1,msgNoOfAmt=msgNoOfAmt,resmetric=resmetric1,summary=summary,sumheader=sumheader,sumsg=sumsg,
		assweight=assweight,asswgtmsg=asswgtmsg)


@app.route('/getweightofamt',methods=['POST', 'GET'])
def getweightofamt():
	if request.method=="POST":
			result=request.form
			studentid = result['studentid']
			code_module = result['code_module']
			code_presentation = result['code_presentation']
			assessmenttype = result['assessmenttype']
			query1="select * from getWeightageInfoOfAssessmentInCourse(%s,%s,%s)"
			tupl1=(code_module,code_presentation,assessmenttype)
			print('tupl1 - ',tupl1)
			print('studentif - ',studentid)
			header=["AssessmentId","Weightage"]
			cur.execute(query1,tupl1)
			result=cur.fetchall()
			rsize=len(result)
			flag=1
			cntmsg="all"
			if rsize ==0 :
				flag=0
				cntmsg="There is no result for given value."
			print('RESULT - ',result)
			msgresult = "All the assessment id of "+assessmenttype+" for course "+code_module+" "+code_presentation
			print('kyu nhi jaa rha h ')
			return render_template('student_viewinfo.html',studentid=studentid,tabheader=header,result=result,msgresult=msgresult,
				flag=flag,cntmsg=cntmsg)



@app.route('/getCourseVLEType',methods=['POST','GET'])
def getCourseVLEType():
	if request.method=="POST":
		result=request.form
		studentid = result['studentid']
		code_module = result['code_module']
		code_presentation = result['code_presentation']
		tupl1=(code_module,code_presentation)
		print('tupl1 - ',tupl1)
		print('studentif - ',studentid)
		query1="select * from getCourseVLEType (%s,%s)"
		cur.execute(query1,tupl1)
		result=cur.fetchall()
		header=["WebsiteId","ActivityType"]
		rsize=len(result)
		flag=1
		cntmsg="all"
		if rsize ==0 :
			flag=0
			cntmsg="There is no result for given value."
		# print('result - ',result)
		# print('bhai chal ja')
		msgresult = "All the course vle material of "+code_module+" "+code_presentation+" are as follows :"
		return render_template('student_viewinfo.html',studentid=studentid,tabheader=header,result=result,msgresult=msgresult,
				flag=flag,cntmsg=cntmsg)	


@app.route('/getNoOfCourseVLETypeWise',methods=['POST','GET'])
def getNoOfCourseVLETypeWise():
	if request.method=="POST":
		result=request.form
		studentid = result['studentid']
		code_module = result['code_module']
		code_presentation = result['code_presentation']
		tupl1=(code_module,code_presentation)
		print('tupl1 - ',tupl1)
		print('studentif - ',studentid)
		query1="select * from getNoOfCourseVLETypeWise (%s,%s)"
		cur.execute(query1,tupl1)
		result=cur.fetchall()
		header=["ActivityType","Count of Material"]
		rsize=len(result)
		flag=1
		cntmsg="all"
		if rsize ==0 :
			flag=0
			cntmsg="There is no result for given value."
		# print('result - ',result)
		# print('bhai chal ja')
		msgresult = "The count of each type of vle material of "+code_module+" "+code_presentation+" are as follows :"
		return render_template('student_viewinfo.html',studentid=studentid,tabheader=header,result=result,msgresult=msgresult,
				flag=flag,cntmsg=cntmsg)




# student_allform

@app.route('/student_allform')
def student_allform():
	render_template('index.html')

@app.route('/student_assessmenttype_info')
def student_assessmenttype_info():
	studentid = (dict(request.args))['studentid']
	code_module = (dict(request.args))['code_module']
	code_presentation = (dict(request.args))['code_presentation']
	assessment_type = (dict(request.args))['assessment_type']
	tupl1=(code_module,code_presentation,studentid,assessment_type)
	query1="select id_assessment,weight,score,aswgtscore from stud_wgt_hapass_score where code_module=%s and code_presentation=%s and id_student=%s and assessment_type=%s"
	cur.execute(query1,tupl1)
	result1=cur.fetchall()
	heading1 = "Performance of studentid "+studentid+" in "+assessment_type+" type of assessments for "+code_module+" "+code_presentation
	tupl2=(code_module,code_presentation)

	if assessment_type == 'TMA':
		query2="select * from get_course_tma_studperfor(%s,%s)"
	elif assessment_type == 'CMA':
	    query2="select * from get_course_cma_studperfor(%s,%s)"
	else :
		query2="select * from get_course_exam_studperfor(%s,%s)"

	cur.execute(query2,tupl2)
	result2=cur.fetchall()
	heading2="Summary of "+assessment_type+" type of assessments for "+code_module+" "+code_presentation

	return render_template('student_assessment_info.html',studentid=studentid,code_module=code_module,code_presentation=code_presentation,
		assessment_type=assessment_type,heading1=heading1,result1=result1,heading2=heading2,result2=result2)


		
@app.route('/get_assessment_summary',methods=['POST','GET'])
def get_assessment_summary():
	if request.method=='POST':
		result=request.form
		studentid = result['studentid']
		code_module = result['code_module']
		code_presentation = result['code_presentation']
		assessmentid=result['assessmentid']
		query="select * from get_course_amt_studperfor(%s,%s,%s)"
		tupl1=(code_module,code_presentation,assessmentid)
		cur.execute(query,tupl1)
		result=cur.fetchall()

		header=["Criteria","Score"]
		rsize=len(result)
		flag=1
		cntmsg="all"
		if rsize ==0 :
			flag=0
			cntmsg="There is no result for given value."
		msgresult="Summary of Assessment Id "+assessmentid+" of "+code_module+" "+code_presentation
		return render_template('student_viewinfo.html',studentid=studentid,tabheader=header,result=result,msgresult=msgresult,
				flag=flag,cntmsg=cntmsg)
	
       ######################################## Student ###########################################################################
  

@app.route('/compare_two_course')
def compare_two_course():
	adminid = (dict(request.args))['adminid']
	return render_template('compare_two_course.html',adminid=adminid)


@app.route('/compare_course_gender',methods=['POST','GET'])
def compare_course_gender():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module1 = result['code_module1']
		code_presentation1 = result['code_presentation1']
		gender1 = result['gender1']

		code_module2 = result['code_module2']
		code_presentation2 = result['code_presentation2']
		gender2 = result['gender2']

		if gender1 == 'Male':
			gend1='M'
		else:
		    gend1='F'

		if gender2 == 'Male':
			gend2='M'
		else:
		    gend2='F'

		tupl1=(code_module1,code_presentation1,gend1,code_module2,code_presentation2,gend2)    	

		query="select * from  comp_course_gender(%s,%s,%s,%s,%s,%s)"

		cur.execute(query,tupl1)

		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]	

		msgresult="The result of given comparision for "+gender1+" count of "+code_module1+" "+code_presentation1+" and "+gender2+" count of "+code_module2+" "+code_presentation2
		return render_template('admin_comp_view_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)


@app.route('/compare_course_region',methods=['POST','GET'])
def compare_course_region():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module1 = result['code_module1']
		code_presentation1 = result['code_presentation1']
		region1 = result['region1']

		code_module2 = result['code_module2']
		code_presentation2 = result['code_presentation2']
		region2 = result['region2']

		tupl1=(code_module1,code_presentation1,region1,code_module2,code_presentation2,region2)    	

		query="select * from  comp_course_region(%s,%s,%s,%s,%s,%s)"

		cur.execute(query,tupl1)

		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]	

		msgresult="The result of given comparision for "+region1+" count of "+code_module1+" "+code_presentation1+" and "+region2+" count of "+code_module2+" "+code_presentation2
		return render_template('admin_comp_view_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)



@app.route('/compare_course_high_education',methods=['POST','GET'])
def compare_course_high_education():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module1 = result['code_module1']
		code_presentation1 = result['code_presentation1']
		high_education1 = result['high_education1']

		code_module2 = result['code_module2']
		code_presentation2 = result['code_presentation2']
		high_education2 = result['high_education2']

		tupl1=(code_module1,code_presentation1,high_education1,code_module2,code_presentation2,high_education2)    	

		query="select * from  comp_course_highest_education(%s,%s,%s,%s,%s,%s)"

		cur.execute(query,tupl1)

		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]	

		msgresult="The result of given comparision for "+high_education1+" count of "+code_module1+" "+code_presentation1+" and "+high_education2+" count of "+code_module2+" "+code_presentation2
		return render_template('admin_comp_view_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)


@app.route('/compare_course_imd_band',methods=['POST','GET'])
def compare_course_imd_band():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module1 = result['code_module1']
		code_presentation1 = result['code_presentation1']
		imd_band1 = result['imd_band1']

		code_module2 = result['code_module2']
		code_presentation2 = result['code_presentation2']
		imd_band2 = result['imd_band2']

		tupl1=(code_module1,code_presentation1,imd_band1,code_module2,code_presentation2,imd_band2)    	

		query="select * from  comp_course_imd_band(%s,%s,%s,%s,%s,%s)"

		cur.execute(query,tupl1)

		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]	

		msgresult="The result of given comparision for "+imd_band1+" count of "+code_module1+" "+code_presentation1+" and "+imd_band2+" count of "+code_module2+" "+code_presentation2
		return render_template('admin_comp_view_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)

@app.route('/compare_course_age_band',methods=['POST','GET'])
def compare_course_age_band():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module1 = result['code_module1']
		code_presentation1 = result['code_presentation1']
		age_band1 = result['age_band1']

		code_module2 = result['code_module2']
		code_presentation2 = result['code_presentation2']
		age_band2 = result['age_band2']

		tupl1=(code_module1,code_presentation1,age_band1,code_module2,code_presentation2,age_band2)    	

		query="select * from  comp_course_age_band(%s,%s,%s,%s,%s,%s)"

		cur.execute(query,tupl1)

		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]	

		msgresult="The result of given comparision for "+age_band1+" count of "+code_module1+" "+code_presentation1+" and "+age_band2+" count of "+code_module2+" "+code_presentation2
		return render_template('admin_comp_view_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)


@app.route('/compare_course_disability',methods=['POST','GET'])
def compare_course_disability():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module1 = result['code_module1']
		code_presentation1 = result['code_presentation1']
		Disability1 = result['Disability1']

		code_module2 = result['code_module2']
		code_presentation2 = result['code_presentation2']
		Disability2 = result['Disability2']

		if Disability1=='Yes':
			disb1='Y'
		else:
		    disb1='N'

		if Disability2=='Yes':
		   disb2='Y'
		else:
		   disb2='N'      	

		tupl1=(code_module1,code_presentation1,disb1,code_module2,code_presentation2,disb2)    	

		query="select * from  comp_course_disability(%s,%s,%s,%s,%s,%s)"

		cur.execute(query,tupl1)

		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]	

		msgresult="The result of given comparision for "+Disability1+" count of "+code_module1+" "+code_presentation1+" and "+Disability2+" count of "+code_module2+" "+code_presentation2
		return render_template('admin_comp_view_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)

@app.route('/course_vle_info')
def course_vle_info():
	adminid = (dict(request.args))['adminid']
	query="select * from get_visit order by code_module,code_presentation"
	cur.execute(query)
	output=cur.fetchall()
	heading="Total sum click on the course vle material by the students for various courses :"
	return render_template('course_vle_info.html',adminid=adminid,output=output,heading=heading)


@app.route('/course_vle_form')
def course_vle_form():
	adminid = (dict(request.args))['adminid']
	code_module = (dict(request.args))['code_module']
	code_presentation = (dict(request.args))['code_presentation']
	return render_template('course_vle_form.html',adminid=adminid,code_module=code_module,code_presentation=code_presentation)	


@app.route('/get_stud_visit',methods=['POST','GET'])
def get_stud_visit():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module = result['code_module']
		code_presentation = result['code_presentation']
		studentid = result['studentid']
		query = "select * from stud_visit(%s,%s,%s)"
		tupl=(code_module,code_presentation,studentid)
		cur.execute(query,tupl)
		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]

		msgresult="The total sum click of "+studentid+" for "+code_module+" "+code_presentation+" are : "
		return render_template('admin_vle_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)


@app.route('/get_stud_day_visit',methods=['POST','GET'])
def get_stud_day_visit():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module = result['code_module']
		code_presentation = result['code_presentation']
		studentid = result['studentid']
		date = result['date']
		query = "select * from stud_day_visit (%s,%s,%s,%s)"
		tupl=(code_module,code_presentation,studentid,date)
		cur.execute(query,tupl)
		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]

		msgresult="The total sum click of "+studentid+" on the day no "+date+" for "+code_module+" "+code_presentation+" are : "
		return render_template('admin_vle_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)


@app.route('/get_stud_act_day_visit',methods=['POST','GET'])
def get_stud_act_day_visit():
	if request.method=='POST':
		result=request.form
		adminid=result['adminid']
		code_module = result['code_module']
		code_presentation = result['code_presentation']
		studentid = result['studentid']
		siteid = result['siteid']
		date = result['date']
		query = "select * from stud_act_day_visit(%s,%s,%s,%s,%s)"
		tupl=(code_module,code_presentation,studentid,siteid,date)
		cur.execute(query,tupl)
		result=cur.fetchall()

		flag=1
		cntmsg='All'

		if len(result)==0:
			flag=0
			cntmsg='No record for given values '
		else:
		    result=result[0][0]

		msgresult="The total sum click of "+studentid+" for siteid "+siteid+" on the day no "+date+" for "+code_module+" "+code_presentation+" are : "
		return render_template('admin_vle_info.html',adminid=adminid,flag=flag,cntmsg=cntmsg,result=result,msgresult=msgresult)	




###############      by anant end ####################


# by PKS start ##########
@app.route('/teacherinfo')
def teacherinfo():
	idteacher = (dict(request.args))['teacher_id']
	query1="SELECT id_teacher,name,profile,qualification, about,expertise, email, phone_no  from teacher where id_teacher=%s"
	cur.execute(query1,(idteacher,))
	rows = cur.fetchall()
	for row in rows:
		print ("ID = ", row[0])
		print ("NAME = ", row[1])
		print ("Profile = ", row[2])
		print ("Email = ", row[6])
		print ("Qualification = ", row[3], "\n")

	# return render_template('teacher_profile.html', rows = rows[0])
	print("calling new gui")
	return render_template('teacher_profile_new.html', teacherid=row[0],output=row)


@app.route('/teachercourse')
def teachercourse():
	idteacher = (dict(request.args))['teacher_id']
	query1="SELECT id_teacher,code_module, code_presentation, subject_name,(select commencement_date from course_commencement_date where course_commencement_date.code_presentation=teacher_course.code_presentation) from teacher_course where id_teacher=%s"
	cur.execute(query1,(idteacher,))
	rows = cur.fetchall()
	for row in rows:
		print ("ID = ", row[0])
		print ("Code = ", row[1])
		print ("code_presentation = ", row[2])
		print ("subject_name = ", row[3], "\n")
	
	# return render_template('teacher_course.html', rows = rows)
	print("calling new gui")
	return render_template('teacher_course_new.html', teacherid=row[0],output=rows)

@app.route('/teacherassessment')
def teacherassessment():
	idteacher = (dict(request.args))['teacher_id']
	# query1="select t.id_teacher,a.code_module ,a.code_presentation ,id_assessment , assessment_type , (select commencement_date from course_commencement_date where course_commencement_date.code_presentation=t.code_presentation)::date + date as date, weight from assessments a, teacher_course t where a.code_module=t.code_module and a.code_presentation=t.code_presentation and t.id_teacher=%s"
	query1="SELECT id_teacher,code_module, code_presentation, subject_name,(select commencement_date from course_commencement_date where course_commencement_date.code_presentation=teacher_course.code_presentation) from teacher_course where id_teacher=%s"
	
	cur.execute(query1,(idteacher,))
	rows = cur.fetchall()
	for row in rows:
		print ("id_teacher = ", row[0])
		print ("Code = ", row[1])
		print ("code_presentation = ", row[3], "\n")
		print ("subject_name = ", row[3], "\n")

	# return render_template('teacher_assessment.html', rows = rows)
	return render_template('teacher_assessment_new.html', teacherid=row[0],output=rows)

@app.route('/liststudent')
def liststudent():
	idteacher = (dict(request.args))['teacher_id']
	# query1="SELECT s.code_module , s.code_presentation ,s.id_student ,(select name from student_name_info where student_name_info.id_student=s.id_student) as name, gender , region, highest_education , imd_band,age_band ,num_of_prev_attempts, studied_credits, disability ,final_result from studentinfo s,teacher_course t where s.code_module=t.code_module and s.code_presentation=t.code_presentation and id_teacher=%s"
	query1="SELECT id_teacher,code_module, code_presentation, subject_name,(select commencement_date from course_commencement_date where course_commencement_date.code_presentation=teacher_course.code_presentation) from teacher_course where id_teacher=%s"
	cur.execute(query1,(idteacher,))
	rows = cur.fetchall()
	#return render_template('list_student_new.html',teacherid=idteacher,output=rows, flag="All Student")
	return render_template('teacher_student_new.html',teacherid=idteacher,output=rows, flag="All Student")

@app.route('/listtopstudent')
def listtopstudent():
	idteacher = (dict(request.args))['teacher_id']
	query1="SELECT s.code_module , s.code_presentation ,s.id_student ,(select name from student_name_info where student_name_info.id_student=s.id_student) as name, gender , region, highest_education , imd_band,age_band ,num_of_prev_attempts, studied_credits, disability ,final_result from studentinfo s,teacher_course t where s.code_module=t.code_module and s.code_presentation=t.code_presentation and final_result='Distinction' and id_teacher=%s"
	cur.execute(query1,(idteacher,))
	rows = cur.fetchall()
	# return render_template("list_student.html",rows = rows)
	return render_template('list_student_new.html',teacherid=idteacher,output=rows,flag="Topper Student")

@app.route('/listfailstudent')
def listfailstudent():
	idteacher = (dict(request.args))['teacher_id']
	query1="SELECT s.code_module , s.code_presentation ,s.id_student ,(select name from student_name_info where student_name_info.id_student=s.id_student) as name, gender , region, highest_education , imd_band,age_band ,num_of_prev_attempts, studied_credits, disability ,final_result from studentinfo s,teacher_course t where s.code_module=t.code_module and s.code_presentation=t.code_presentation and (final_result='Fail' or final_result='Withdrawn') and id_teacher=%s"
	cur.execute(query1,(idteacher,))
	rows = cur.fetchall()
	# return render_template("list_student.html",rows = rows)
	return render_template('list_student_new.html',teacherid=idteacher,output=rows,flag="Fail/Withdrawn Student")

@app.route('/teachercoursedetail')
def teachercoursedetail():
	idteacher = (dict(request.args))['teacher_id']
	codemodule = (dict(request.args))['code_module']
	codepresentation = (dict(request.args))['code_presentation']
	
	query1ResultWiseStudentCount="SELECT * from getResultWiseStudentCount(%s,%s)"
	cur.execute(query1ResultWiseStudentCount,(codemodule,codepresentation))
	rowsResultWiseStudentCount = cur.fetchall()
	print("size of rowsResultWiseStudentCount:",len(rowsResultWiseStudentCount))

	query1GenderWiseStudentCount="SELECT * from getStudentGenderCount(%s,%s)"
	cur.execute(query1GenderWiseStudentCount,(codemodule,codepresentation))
	rowsGenderWiseStudentCount = cur.fetchall()

	query1RegionWiseStudentCount="SELECT * from getNoOfStudentRegionWise(%s,%s)"
	cur.execute(query1RegionWiseStudentCount,(codemodule,codepresentation))
	rowsRegionWiseStudentCount = cur.fetchall()
	
	query1HtEdWiseStudentCount="SELECT * from getNoOfStudentHtEducationWise(%s,%s)"
	cur.execute(query1HtEdWiseStudentCount,(codemodule,codepresentation))
	rowsHtEdWiseStudentCount = cur.fetchall()
	
	query1IMDBandWiseStudentCount="SELECT * from getNoOfStudentIMDBandWise(%s,%s)"
	cur.execute(query1IMDBandWiseStudentCount,(codemodule,codepresentation))
	rowsIMDBandWiseStudentCount = cur.fetchall()
	
	query1AgeBandWiseStudentCount="SELECT * from getNoOfStudentAgeBandWise(%s,%s)"
	cur.execute(query1AgeBandWiseStudentCount,(codemodule,codepresentation))
	rowsAgeBandWiseStudentCount = cur.fetchall()

	query1DisabledStudentCount="SELECT * from getNoOfStudentDisabled(%s,%s)"
	cur.execute(query1DisabledStudentCount,(codemodule,codepresentation))
	rowsDisabledStudentCount = cur.fetchall()

	query1RegAfterCourseStStudentCount="SELECT * from getNoOfStudentRegisteredAfterCourseStart(%s,%s)"
	cur.execute(query1RegAfterCourseStStudentCount,(codemodule,codepresentation))
	rowsRegAfterCourseStStudentCount = cur.fetchall()

	query1WithdrawnStudentCount="SELECT * from getNoOfStudentWithdrawnCourse(%s,%s)"
	cur.execute(query1WithdrawnStudentCount,(codemodule,codepresentation))
	rowsWithdrawnStudentCount = cur.fetchall()

	query1StudentCount="SELECT * from get_course_strength(%s,%s)"
	cur.execute(query1StudentCount,(codemodule,codepresentation))
	rowsStudentCount = cur.fetchall()

	query1CourseVLEVisit="SELECT * from coursevle_visit(%s,%s)"
	cur.execute(query1CourseVLEVisit,(codemodule,codepresentation))
	rowsCourseVLEVisit = cur.fetchall()

	query1StudentResultPercent="SELECT * from getPercentageOfStudentResultWise(%s,%s)"
	cur.execute(query1StudentResultPercent,(codemodule,codepresentation))
	rowsStudentResultPercent = cur.fetchall()

	query1StudentResultSummary="select \'Average\' as Criteria,(avg(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s union select \'Minimum\' as Criteria,(min(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s union select \'Maximum\' as Criteria,(max(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s" 
	cur.execute(query1StudentResultSummary,(codemodule,codepresentation,codemodule,codepresentation,codemodule,codepresentation))
	rowsStudentResultSummary = cur.fetchall()
	print("size of rowsStudentResultSummary:",len(rowsStudentResultSummary))

	query1CourseExamWt="select stud_asthaptype_agsco.assessment_type,(stud_asthaptype_agsco.agrweight::NUMERIC) from stud_asthaptype_agsco where stud_asthaptype_agsco.code_module=%s and stud_asthaptype_agsco.code_presentation=%s GROUP BY stud_asthaptype_agsco.assessment_type,stud_asthaptype_agsco.agrweight"
	cur.execute(query1CourseExamWt,(codemodule,codepresentation))
	rowsCourseExamWt = cur.fetchall()

	query1CourseVleCount="select * from get_course_vle_cnt(%s,%s)"
	cur.execute(query1CourseVleCount,(codemodule,codepresentation))
	rowsCourseVleCount = cur.fetchall()

	# return render_template("list_student.html",rows = rows)
	return render_template('teacher_course_detail.html',teacherid=idteacher, codemodule =codemodule,codepresentation=codepresentation,
		rowsResultWiseStudentCount=rowsResultWiseStudentCount, 
		rowsGenderWiseStudentCount=rowsGenderWiseStudentCount,
		rowsRegionWiseStudentCount=rowsRegionWiseStudentCount, 
		rowsHtEdWiseStudentCount=rowsHtEdWiseStudentCount,
		rowsIMDBandWiseStudentCount=rowsIMDBandWiseStudentCount,
		rowsAgeBandWiseStudentCount=rowsAgeBandWiseStudentCount,
		rowsDisabledStudentCount=rowsDisabledStudentCount[0],
		rowsRegAfterCourseStStudentCount=rowsRegAfterCourseStStudentCount[0],
		rowsWithdrawnStudentCount=rowsWithdrawnStudentCount[0],
		rowsStudentCount=rowsStudentCount[0],
		rowsCourseVLEVisit=rowsCourseVLEVisit[0],
		rowsStudentResultPercent=rowsStudentResultPercent,
		rowsStudentResultSummary=rowsStudentResultSummary,
		rowsCourseExamWt=rowsCourseExamWt,
		rowsCourseVleCount=rowsCourseVleCount
		
		)

@app.route('/teacherassessdetail')
def teacherassessdetail():
	idteacher = (dict(request.args))['teacher_id']
	codemodule = (dict(request.args))['code_module']
	codepresentation = (dict(request.args))['code_presentation']
	
	# query1="SELECT id_teacher,code_module, code_presentation, subject_name,(select commencement_date from course_commencement_date where course_commencement_date.code_presentation=teacher_course.code_presentation) from teacher_course where id_teacher=%s and code_module=%s and code_presentation=%s"
	query1="select a.code_module ,a.code_presentation ,id_assessment , assessment_type , (select commencement_date from course_commencement_date where course_commencement_date.code_presentation=t.code_presentation)::date + date as date, weight from assessments a, teacher_course t where a.code_module=t.code_module and a.code_presentation=t.code_presentation and t.id_teacher=%s and a.code_module=%s and a.code_presentation=%s"
	cur.execute(query1,(idteacher,codemodule,codepresentation))
	rowsAssessment = cur.fetchall()

	query2="select sa.id_assessment, sa.id_student, (select commencement_date from course_commencement_date where course_commencement_date.code_presentation=t.code_presentation)::date +date_submitted, score from  studentassessment sa, assessments a,teacher_course t where a.code_module=t.code_module and a.code_presentation=t.code_presentation and a.id_assessment=sa.id_assessment and t.id_teacher=%s and a.code_module=%s and a.code_presentation=%s"
	cur.execute(query2,(idteacher,codemodule,codepresentation))
	rowsSubmission = cur.fetchall()

	query3="select code_module,code_presentation,id_assessment,assessment_type, date, weight from not_happen_esment where code_module=%s and code_presentation=%s"
	cur.execute(query3,(codemodule,codepresentation))
	rowsAssessmentNotHeld = cur.fetchall()

	query4="select code_module,code_presentation,id_student,student_name,assessment_type,agrweight,agrscore from stud_asthaptype_agsco where code_module=%s and code_presentation=%s"
	cur.execute(query4,(codemodule,codepresentation))
	rowsAggregateScore = cur.fetchall()

	query1CourseExamWt="select stud_asthaptype_agsco.assessment_type,(stud_asthaptype_agsco.agrweight::NUMERIC) from stud_asthaptype_agsco where stud_asthaptype_agsco.code_module=%s and stud_asthaptype_agsco.code_presentation=%s GROUP BY stud_asthaptype_agsco.assessment_type,stud_asthaptype_agsco.agrweight"
	cur.execute(query1CourseExamWt,(codemodule,codepresentation))
	rowsCourseExamWt = cur.fetchall()

	print("size of rowsCourseExamWt:",len(rowsCourseExamWt))
	return render_template('teacher_assess_detail.html',teacherid=idteacher, codemodule =codemodule,codepresentation=codepresentation,
		rowsAssessment=rowsAssessment,
		rowsSubmission=rowsSubmission,
		rowsAssessmentNotHeld=rowsAssessmentNotHeld,
		rowsAggregateScore=rowsAggregateScore,
		rowsCourseExamWt=rowsCourseExamWt
		)

@app.route('/teacherstudentdetail')
def teacherstudentdetail():
	idteacher = (dict(request.args))['teacher_id']
	codemodule = (dict(request.args))['code_module']
	codepresentation = (dict(request.args))['code_presentation']

	query1CourseStudent="select studentid,studentname,result from get_course_student(%s,%s) "
	cur.execute(query1CourseStudent,(codemodule,codepresentation))
	rowsCourseStudent = cur.fetchall()

	query1ResultWiseStudentCount="SELECT * from getResultWiseStudentCount(%s,%s)"
	cur.execute(query1ResultWiseStudentCount,(codemodule,codepresentation))
	rowsResultWiseStudentCount = cur.fetchall()
	print("size of rowsResultWiseStudentCount:",len(rowsResultWiseStudentCount))

	query1GenderWiseStudentCount="SELECT * from getStudentGenderCount(%s,%s)"
	cur.execute(query1GenderWiseStudentCount,(codemodule,codepresentation))
	rowsGenderWiseStudentCount = cur.fetchall()

	query1RegionWiseStudentCount="SELECT * from getNoOfStudentRegionWise(%s,%s)"
	cur.execute(query1RegionWiseStudentCount,(codemodule,codepresentation))
	rowsRegionWiseStudentCount = cur.fetchall()
	
	query1HtEdWiseStudentCount="SELECT * from getNoOfStudentHtEducationWise(%s,%s)"
	cur.execute(query1HtEdWiseStudentCount,(codemodule,codepresentation))
	rowsHtEdWiseStudentCount = cur.fetchall()
	
	query1IMDBandWiseStudentCount="SELECT * from getNoOfStudentIMDBandWise(%s,%s)"
	cur.execute(query1IMDBandWiseStudentCount,(codemodule,codepresentation))
	rowsIMDBandWiseStudentCount = cur.fetchall()
	
	query1AgeBandWiseStudentCount="SELECT * from getNoOfStudentAgeBandWise(%s,%s)"
	cur.execute(query1AgeBandWiseStudentCount,(codemodule,codepresentation))
	rowsAgeBandWiseStudentCount = cur.fetchall()

	query1DisabledStudentCount="SELECT * from getNoOfStudentDisabled(%s,%s)"
	cur.execute(query1DisabledStudentCount,(codemodule,codepresentation))
	rowsDisabledStudentCount = cur.fetchall()

	query1RegAfterCourseStStudentCount="SELECT * from getNoOfStudentRegisteredAfterCourseStart(%s,%s)"
	cur.execute(query1RegAfterCourseStStudentCount,(codemodule,codepresentation))
	rowsRegAfterCourseStStudentCount = cur.fetchall()

	query1WithdrawnStudentCount="SELECT * from getNoOfStudentWithdrawnCourse(%s,%s)"
	cur.execute(query1WithdrawnStudentCount,(codemodule,codepresentation))
	rowsWithdrawnStudentCount = cur.fetchall()

	query1StudentCount="SELECT * from get_course_strength(%s,%s)"
	cur.execute(query1StudentCount,(codemodule,codepresentation))
	rowsStudentCount = cur.fetchall()

	query1CourseVLEVisit="SELECT * from coursevle_visit(%s,%s)"
	cur.execute(query1CourseVLEVisit,(codemodule,codepresentation))
	rowsCourseVLEVisit = cur.fetchall()

	query1StudentResultPercent="SELECT * from getPercentageOfStudentResultWise(%s,%s)"
	cur.execute(query1StudentResultPercent,(codemodule,codepresentation))
	rowsStudentResultPercent = cur.fetchall()

	query1StudentResultSummary="select \'Average\' as Criteria,(avg(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s union select \'Minimum\' as Criteria,(min(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s union select \'Maximum\' as Criteria,(max(stud_fs_result.finalscore)::numeric) from stud_fs_result where stud_fs_result.code_module=%s and stud_fs_result.code_presentation=%s" 
	cur.execute(query1StudentResultSummary,(codemodule,codepresentation,codemodule,codepresentation,codemodule,codepresentation))
	rowsStudentResultSummary = cur.fetchall()
	print("size of rowsStudentResultSummary:",len(rowsStudentResultSummary))

	query1CourseExamWt="select stud_asthaptype_agsco.assessment_type,(stud_asthaptype_agsco.agrweight::NUMERIC) from stud_asthaptype_agsco where stud_asthaptype_agsco.code_module=%s and stud_asthaptype_agsco.code_presentation=%s GROUP BY stud_asthaptype_agsco.assessment_type,stud_asthaptype_agsco.agrweight"
	cur.execute(query1CourseExamWt,(codemodule,codepresentation))
	rowsCourseExamWt = cur.fetchall()

	query1CourseVleCount="select * from get_course_vle_cnt(%s,%s)"
	cur.execute(query1CourseVleCount,(codemodule,codepresentation))
	rowsCourseVleCount = cur.fetchall()

	return render_template('teacher_student_detail.html',teacherid=idteacher, codemodule =codemodule,codepresentation=codepresentation,
		rowsCourseStudent=rowsCourseStudent,
		rowsResultWiseStudentCount=rowsResultWiseStudentCount, 
		rowsGenderWiseStudentCount=rowsGenderWiseStudentCount,
		rowsRegionWiseStudentCount=rowsRegionWiseStudentCount, 
		rowsHtEdWiseStudentCount=rowsHtEdWiseStudentCount,
		rowsIMDBandWiseStudentCount=rowsIMDBandWiseStudentCount,
		rowsAgeBandWiseStudentCount=rowsAgeBandWiseStudentCount,
		rowsDisabledStudentCount=rowsDisabledStudentCount[0],
		rowsRegAfterCourseStStudentCount=rowsRegAfterCourseStStudentCount[0],
		rowsWithdrawnStudentCount=rowsWithdrawnStudentCount[0],
		rowsStudentCount=rowsStudentCount[0],
		rowsCourseVLEVisit=rowsCourseVLEVisit[0],
		rowsStudentResultPercent=rowsStudentResultPercent,
		rowsStudentResultSummary=rowsStudentResultSummary,
		rowsCourseExamWt=rowsCourseExamWt,
		rowsCourseVleCount=rowsCourseVleCount
		)

@app.route('/logout')
def logout():
    # logout_user()
    return redirect(url_for('loginpage'))

# By PKS end ##########

if __name__ == '__main__':
   app.run(debug = True)	



# {{ url_for('cool_form') }}

