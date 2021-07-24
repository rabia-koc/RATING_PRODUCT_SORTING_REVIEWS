# RATING_PRODUCT_SORTING_REVIEWS
 
   ![0_xqeHsgPVLV9t8shX](https://user-images.githubusercontent.com/73841520/126864066-b0351b20-2ba3-4820-95d1-39663414180c.jpg)

# İş Problemi

* Ürün ratinglerini daha doğru hesaplamaya çalışmak ve ürün yorumlarını daha doğru sıralamak.
* Buradaki ana odağımız, insanların ilgili yorumu puanından bağımsız bir şekilde faydalı bulup bulmamasıdır. Pazarı manipüle etmeden gerçekte olanı yansıtarak yorumları %5 hata payı ile modellemeyi gerçekleştirmek.  

# Veri Seti Hikayesi

* Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
* Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

# Değişkenler

* reviewerID ---> Kullanıcı ID’si
  * Örn: A2SUAM1J3GNN3B
* asin --–> Ürün ID’si
  * Örn: 0000013714
* reviewerName --–> Kullanıcı Adı  
* helpful --–> Faydalı yorum derecesi  
  * Örn: 2/3
* reviewText --–> Yorum
  * Kullanıcının yazdığı inceleme metni
* overall --–> Ürün rating’i
* summary --–> İnceleme özeti
* unixReviewTime --–> İnceleme zamanı
  * Unix time
* reviewTime --–> İnceleme zamanı
  * Raw
