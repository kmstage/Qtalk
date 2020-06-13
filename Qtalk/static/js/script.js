function handleResponse(data){
  var id = data.post_id
  var new_result = data.result
  $('#result-'+ id ).html(new_result)

if (data.state == 'like') {
    $('#like-'+ id).css('display', 'none')
    $('#dislike-'+ id).css('display', 'none')
    $('#unlike-'+ id).css('display', 'inline')
    $('#undislike-'+ id).css('display', 'none')
} else if (data.state == 'dislike') {
    $('#like-'+ id).css('display', 'none')
    $('#dislike-'+ id).css('display', 'none')
    $('#unlike-'+ id).css('display', 'none')
    $('#undislike-'+ id).css('display', 'inline')
} else if (data.state == 'unlike'){
    $('#like-'+ id).css('display', 'inline')
    $('#dislike-'+ id).css('display', 'inline')
    $('#unlike-'+ id).css('display', 'none')
    $('#undislike-'+ id).css('display', 'none')
} else if (data.state == 'undislike'){
    $('#like-'+ id).css('display', 'inline')
    $('#dislike-'+ id).css('display', 'inline')
    $('#unlike-'+ id).css('display', 'none')
    $('#undislike-'+ id).css('display', 'none')
}
}

function likeClick(e){
  var fid = $(this).attr('id');
  var id = fid.slice(5)
  $.ajax('/like/'+ id +'/like',{
    type: 'GET',
    success: handleResponse
  });
}

function dislikeClick(e){
  var fid = $(this).attr('id');
  var id = fid.slice(8)
  $.ajax('/dislike/'+ id +'/dislike',{
    type: 'GET',
    success: handleResponse
  });
}

function unlikeClick(e){
  var fid = $(this).attr('id');
  var id = fid.slice(7)
  $.ajax('/like/'+ id +'/unlike',{
    type: 'GET',
    success: handleResponse
  });
}

function undislikeClick(e){
  var fid = $(this).attr('id');
  var id = fid.slice(10)
  $.ajax('/dislike/'+ id +'/undislike',{
    type: 'GET',
    success: handleResponse
  });
}

$(document).ready(function (){

  $('.like_btn').each(function (){
    $(this).click(likeClick);
});
  $('.dislike_btn').each(function (){
    $(this).click(dislikeClick);
});
  $('.unlike_btn').each(function (){
    $(this).click(unlikeClick);
});
  $('.undislike_btn').each(function (){
    $(this).click(undislikeClick);
});
})
