import java.io.IOException;
import java.net.MalformedURLException;
import twitter4j.*;
import java.net.URL;
import java.nio.channels.Channels;
import java.nio.channels.ReadableByteChannel;
import java.io.FileOutputStream;
import java.text.DateFormat;
import java.text.SimpleDateFormat;

import java.awt.image.BufferedImage;
import java.awt.Graphics;
import java.io.File;

import javax.imageio.ImageIO;

import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;


/**
 * Twitter4Jで検索結果の画像を取得してみるサンプル
 * @author kikutaro
 */

public class PictGet{
	//取得件数
	static final int TWEET_NUM = 100;
    
	//保存対象の画像拡張子
	static final String TARGET_EXTENSION = ".jpg";

	//保存枚数
	static final int PICT_MAX=2000;
        
	public static void main( String[] args ) throws ParseException , TwitterException , MalformedURLException , IOException {
		//フォルダ作成
		File save_file = new File("./Timeline");
		if (save_file.mkdir()){
			System.out.println("maked directry ./Timeline");
		}
		save_file = new File("./Timeline/all");
		if (save_file.mkdir()){
			System.out.println("maked directry ./Pictur/all");
		}
		int PICT_NUM=0;
		int rem_PICT_NUM=0;
		long next_id=-1;
		long rem_id=-1;
		DateFormat df = new SimpleDateFormat("HHmmssSSS");
		Date dt = new Date();
		Calendar cal = Calendar.getInstance();
		Twitter twitter = new TwitterFactory().getInstance();
		ResponseList<Status> statuses = null;
		Paging pages = null;
		// 最後に取得したステータスID
		long lastStatusId = 0;

		while (true) {
			if (pages == null) {
				// 初取得時のTL取得の設定
				pages = new Paging(1, 10);
       		        } else {
				// 最後に取得したステータスID以降を取得
				pages = new Paging((long) lastStatusId);
			}
			statuses = twitter.getHomeTimeline(pages);
			if (statuses.size()>0){
				lastStatusId=statuses.get(0).getId();
				for (Status sts : statuses) {
					for(MediaEntity media : sts.getMediaEntities()){
						//複数枚投稿かどうかで分岐
						if(sts.getExtendedMediaEntities().length>0){
							for(MediaEntity exmedia : sts.getExtendedMediaEntities()){
								PICT_NUM=saver(sts,media,PICT_NUM,df);
							}
						}else{
							PICT_NUM=saver(sts,media,PICT_NUM,df);
						}
					}
					next_id = sts.getId();
					dt = sts.getCreatedAt();
				}
			}
			cal.setTime(dt);
			cal.add(Calendar.DATE, 1);
			System.out.printf(next_id+"%n");
			System.out.printf(df.format(cal.getTime())+"%n");
			try{
				Thread.sleep(90000); //90秒Sleepする
			}catch(InterruptedException e){
			}
		}
	}

	//保存処理クラス
	public static int saver(Status sts,MediaEntity media,int PICT_NUM,DateFormat df) throws MalformedURLException, IOException {
		if(PICT_NUM>=PICT_MAX||PICT_NUM<=-1){
			return -1;
		}
		//ファボ数でフィルタする場合は，if(sts.getFavoriteCount() > 5)         	
		//とりあえず拡張子だけでフィルタ
		if(media.getMediaURL().endsWith(".jpg")||media.getMediaURL().endsWith(".png")||media.getMediaURL().endsWith(".bmp")){
			//エラーのときは保存すらできない？
			try{
				URL website = new URL(media.getMediaURL());
				//保存
				String file_name = String.format("./Timeline/all/"+df.format(sts.getCreatedAt())+".jpg");
				BufferedImage image = ImageIO.read(website.openConnection().getInputStream());
				int ww=image.getWidth();
				int hh=image.getHeight();
				BufferedImage image2=new BufferedImage(ww,hh,BufferedImage.TYPE_INT_RGB);
				Graphics g2=image2.getGraphics();
				g2.drawImage(image,0,0,null);
				g2.dispose();
				ImageIO.write(image2, "jpeg", new File(file_name));
				System.out.printf("saved "+file_name+"%n");
				PICT_NUM++;
			}catch(Exception e){
			}
		}
		return PICT_NUM;
	}
}
