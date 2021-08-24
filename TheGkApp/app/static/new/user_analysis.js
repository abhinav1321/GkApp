




// get_overall_details_for_user_analysis


// subject_list_user_analysis
function doTheThing() {
return new Promise((resolve, reject) => {
 $.ajax({
    type: "POST",
    url: 'get_subjects_for_user_analysis',
    data: {
    	'username' : username,
    	'csrfmiddlewaretoken':csrftoken,
    	  },
    success: function(response){
        //if request if made successfully then the response represent the data
        console.log(response);
        var subjects = response['data'];
        console.log(subjects, 'Subjects List');
        resolve(subjects);
    },
    error : function(error){
    reject(error);
    },
});
})}


function doOther(subjects) {

return new Promise((resolve, reject) => {
var i;
for (i = 0; i < subjects.length; i++) {
	console.log(subjects[i], 'subejcts');
$.ajax({
    type: "POST",
    url: 'topic_details_user_analysis',
    data: {
    	'username' : username,
    	'subject': subjects[i],
    	'csrfmiddlewaretoken':csrftoken,
    	  },
    success: function(response){


        //if request if made successfully then the response represent the data
        console.log(response,'2nd response');
    },
    error : function(error){
    	console.log(error);
    reject(error);
    },

});
}

})
}


doTheThing()
.then((data) => {
console.log('2nd function');
console.log(data, 'data here');
	doOther(data);
// get_topics_for_user_analysis
 } )

.catch((error) => {
    console.log(error)
  })







// get_subject_details_for_user_analysis
//
//
// get_topics_details_for_user_analysis

