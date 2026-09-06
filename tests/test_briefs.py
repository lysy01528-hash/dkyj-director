import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'addon'))
from scene_briefs import BriefStore
class BriefTests(unittest.TestCase):
    def test_roundtrip_idempotency_and_completion(self):
        with tempfile.TemporaryDirectory() as root:
            store=BriefStore(root);e=dict(id='brief-example',scene='小船',characters='1 人',action='跑向甲板',camera='跟拍',source='steamship')
            store.create(e);store.create(e);self.assertEqual(len(store.data['items']),1)
            store.update(dict(id=e['id'],status='needs_input',message='几秒？'))
            store.reply(dict(id=e['id'],message='10 秒'))
            store=BriefStore(root);self.assertEqual(store.find(e['id'])['status'],'waiting');self.assertEqual(store.find(e['id'])['messages'][-1]['text'],'10 秒')
            with self.assertRaises(ValueError):store.update(dict(id=e['id'],status='ready'))
            store.update(dict(id=e['id'],status='working',project_id='test'))
            with self.assertRaises(ValueError):store.reply(dict(id=e['id'],message='race'))
            store.update(dict(id=e['id'],status='ready',verification='Inspected frame 1 and 240'))
            self.assertEqual(BriefStore(root).find(e['id'])['verification'],'Inspected frame 1 and 240')
    def test_invalid_briefs(self):
        with tempfile.TemporaryDirectory() as root:
            store=BriefStore(root)
            for e in [{'id':'../outside'},{'id':'brief-empty','scene':'x'}]:
                with self.assertRaises(ValueError):store.create(e)
            self.assertFalse(store.data['items'])
if __name__=='__main__':unittest.main()
