import hddm
import pickle
data = hddm.load_csv('simple_difficulty.csv')
m = hddm.HDDM(data)
m.sample(500, db='pickle', dbname='db.pickle')
#pickle.dump(m, open('tmp.pickle', 'w'))
#pickle.load(open('tmp.pickle', 'r'))
m.save('tmp.pickle')
import kabuki
kabuki.utils.load('tmp.pickle')
