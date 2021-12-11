$( document ).ready(function() {
	console.log(studentid)
	$.ajax({
                type:"post",
                async:false,
                dataType: 'json',
                contentType:"application/json",
                data:JSON.stringify({"student_id":studentid}),
                url:"/get_student_basic_info",
                processData: false,
                success: function(data){
                	console.log(data);
                        var data_arr = data["data"]
                        var course_arr=data["rekourse"]
                        var name = "Hello "+ data_arr[1]
                        $("#info1").html(name);
                	
                },
                error: function(err){

                }
	})
});

