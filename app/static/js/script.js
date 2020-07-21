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

function followResponse(data){
  var username = data.target
  var follower = data.follower
  var following = data.following
  $('#following_count-'+ username).html(following)
  $('#followers_count-'+ username).html(follower)
  if (data.result == 'followed') {
      $('#u-'+ username).css('display', 'inline')
      $('#f-'+ username).css('display', 'none')

  } else if (data.result == 'unfollowed') {
      $('#u-'+ username).css('display', 'none')
      $('#f-'+ username).css('display', 'inline')
}
}

function deleteComment(data){
  var comment_id = data.comment_id 
  $('#comment-'+ comment_id).css('display', 'none')
  var modal = $('#deleteCommentModal');
  modal.modal('hide');
}

function likeCard(value) {
  card =   `<div class="card border-success mb-3 text-center">
              <div class="card-body text-success ">
                <h5 class="card-title text-success"> <a style="color:#228B22" href="/user/${value}" >${value}</a> </h5>
              </div>
          </div>`
  window.result = window.result + card ;
}
function dislikeCard(value) {
  card =    `<div class="card border-danger mb-3 text-center">
                <div class="card-body" text-danger>
                  <h5 class="card-title text-danger"> <a style="color:#DC143C" href="/user/${value}" >${value}</a> </h5>
                </div>
            </div>`;
  window.result = window.result + card ;
}

function showScoresModal(data){
  window.result = ""
  var modal = $('#scoreModal');
  data.likes.forEach(likeCard)
  data.dislikes.forEach(dislikeCard)
  modal.find('.modal-scores').html(result);
  modal.modal('show');
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

function followActionClick(e){
  var id = $(this).attr('id');
  var username = id.slice(2)
  $.ajax('/follow/'+ username ,{
    type: 'POST',
    success: followResponse
  });
}
function unfollowActionClick(e){
  var id = $(this).attr('id');
  var username = id.slice(2)
  $.ajax('/unfollow/'+ username ,{
    type: 'POST',
    success: followResponse
  });
}
function getScores(e){
  var fid = $(this).attr('id');
  var id = fid.slice(7)
  $.ajax('/post/'+ id + '/scores' ,{
    type: 'POST',
    success: showScoresModal
  });
}
function deleteCommentModal(e){
  var id = $(this).attr('id');
  var result = `
    <button type="button" class="btn btn-secondary" data-dismiss="modal">خروج</button>
    <button type="button" class="btn btn-danger" id="delete-comment-${id}" >حذف</button>
  `
  var modal = $('#deleteCommentModal');
  modal.find('.modal-delete-comment').html(result);
  modal.modal('show');
  $( "#delete-comment-"+ id ).click(function() {
    $.ajax('/delete_comment/'+ id ,{
      type: 'POST',
      success: deleteComment
    });
  });
}

$(document).ready(function (){
      document.emojiButton = 'fa fa-smile-o';
      document.emojiType = 'unicode';
      document.emojiSource = '/static/img';

    $(('[id="summernote"]')).summernote({
      toolbar: [
          ['style', ['bold', 'italic', 'underline', 'clear']],
          ['fontsize', ['fontsize']],
          ['color', ['color']],
          ['insert', ['link', 'picture', 'video', 'emoji']],
          ['para', ['ul', 'ol', 'paragraph']]

],
      tabsize: 2,
      height: 200,
      dialogsInBody: true,
      disableDragAndDrop: true,
      callbacks:{
	  	onImageLinkInsert:function(url){
      $img = $('<img>').attr({ src: url, width:'100%'})
      $(this).summernote('insertNode', $img[0]);
		}
	},
});

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
  $('.Follow').each(function (){
    $(this).click(followActionClick);
});
  $('.unFollow').each(function (){
    $(this).click(unfollowActionClick);
});
  $('.show_score').each(function (){
    $(this).click(getScores);
});
$('.delete_comment_modal').each(function (){
  $(this).click(deleteCommentModal);
});
})
