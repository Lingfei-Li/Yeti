/**
 * Created by Yida Yin on 1/14/18
 */

const timeConverter = (UNIX_timestamp, detailed) => {
  const a = new Date(UNIX_timestamp * 1000);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const year = a.getFullYear();
  const month = months[a.getMonth()];
  const date = a.getDate();
  const hour = a.getHours();
  const min = a.getMinutes();
  const sec = a.getSeconds();
  let dateStr = month + '-' + date + '-' + year;
  if (detailed) {
    dateStr = dateStr + ' ' + hour + ':' + min + ':' + sec;
  }
  return dateStr;
};

export {timeConverter};