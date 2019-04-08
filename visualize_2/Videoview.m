% meshsave contains variables from python
load meshsave_back_2.mat
fullmesh_px = mesh_all;

clc
dbstop if error

% cap
videoFileReader = vision.VideoFileReader('C:\Study\GoPro_Recodring\DataTest20180826\Back\Back_1.MP4.AVI');
videoFrame      = step(videoFileReader);

% face
videoFileReader2 = vision.VideoFileReader('C:\Study\GoPro_Recodring\DataTest20180826\Back\Face_1.MP4.AVI');
videoFrame2      = step(videoFileReader2);

videoInfo    = info(videoFileReader);
ct = 3;
aviobj = VideoWriter('C:\Study\GoPro_Recodring\DataTest20180826\Back\tag_pred_abc_new1234.avi');
open(aviobj);
fr_no = 1;
while ~isDone(videoFileReader)
    ax = figure;
    
    imshow([videoFrame videoFrame2(:,750:end,:)])
    hold on
    for sqc = 1:23
        plot([vismesh_px(sqc*4-3,1,fr_no) vismesh_px(sqc*4-2,1,fr_no)],[vismesh_px(sqc*4-3,2,fr_no) vismesh_px(sqc*4-2,2,fr_no)],'b','linewidth',4)
        plot([vismesh_px(sqc*4-2,1,fr_no) vismesh_px(sqc*4-1,1,fr_no)],[vismesh_px(sqc*4-2,2,fr_no) vismesh_px(sqc*4-1,2,fr_no)],'b','linewidth',4)
        plot([vismesh_px(sqc*4-1,1,fr_no) vismesh_px(sqc*4,1,fr_no)],[vismesh_px(sqc*4-1,2,fr_no) vismesh_px(sqc*4,2,fr_no)],'b','linewidth',4)
        plot([vismesh_px(sqc*4,1,fr_no) vismesh_px(sqc*4-3,1,fr_no)],[vismesh_px(sqc*4,2,fr_no) vismesh_px(sqc*4-3,2,fr_no)],'b','linewidth',4)
    end

    plot([2700 -axis_px(4,1,fr_no)+axis_px(1,1,fr_no)+2700],[500 -axis_px(4,2,fr_no)+axis_px(1,2,fr_no)+500 ],'b','linewidth',2)
    plot([2700 -axis_px(4,1,fr_no)+axis_px(2,1,fr_no)+2700],[500 -axis_px(4,2,fr_no)+axis_px(2,2,fr_no)+500 ],'g','linewidth',2)
    plot([2700 -axis_px(3,1,fr_no)+axis_px(4,1,fr_no)+2700],[500 -axis_px(3,2,fr_no)+axis_px(4,2,fr_no)+500 ],'r','linewidth',2)

    t = text(1,20,['frame number : ' num2str(fr_no)],'FontSize',20,'FontWeight','bold','Color','red');
    F = getframe(ax);
    writeVideo(aviobj,F.cdata);
%     Extract the next video frame
    close all
    videoFrame = step(videoFileReader);
    videoFrame2 = step(videoFileReader2);
    fr_no = fr_no+1;
    if ~mod(fr_no,20)
        fr_no
    end
%     if (fr_no==500)
%         dbstop
%     end
    
end
close(aviobj);
% Release resources
release(videoFileReader);

