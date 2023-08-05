ariblib
=======

速度優先の Transport Stream パーサです。
Python 3.2 での動作が前提ですが、3.1 でも動くかもしれません。

ARIB-STD で定義されているデータ構造をなるべく近い形で
Python コードとして記述できるようにしています。

たとえば、 Program Map Section のデータ構造は ARIB-STD-B10 第2部付録E 表E-3 で
以下のように記述されています:

```
TS_program_map_section(){
    table_id                   8  uimsbf
    section_syntax_indicator   1  bslbf
    ‘0’                        1  bslbf
    reserved                   2  bslbf
    section_length            12  uimsbf
    program_number            16  uimsbf
    reserved                   2  bslbf
    version_number             5  uimsbf
    current_next_indicator     1  bslbf
    section_number             8  uimsbf
    last_section_number        8  uimsbf
    reserved                   3  bslbf
    PCR_PID                   13  uimsbf
    reserved                   4  bslbf
    program_info_length       12  uimsbf
    for (i=0;i<N;i++){
        descriptor()
    }
    for (i=0;i<N1;i++){
        stream_type            8  uimsbf
        reserved               3  bslbf
        elementary_PID        13  uimsbf
        reserved               4  bslbf
        ES_info_length        12  uimsbf
        for (i=0;i<N2;i++){
            descriptor()
        }
    }
    CRC_32                    32 rpchof
```
これを ariblib では以下のように記述します。 (説明に必要でない行は省略しています)
```python

class ProgramMapSection(Section):
    table_id = uimsbf(8)
    section_syntax_indicator = bslbf(1)
    reserved_future_use = bslbf(1)
    reserved_1 = bslbf(2)
    section_length = uimsbf(12)
    program_number = uimsbf(16)
    reserved_2 = bslbf(2)
    version_number = uimsbf(5)
    current_next_indicator = bslbf(1)
    section_number = uimsbf(8)
    last_section_number = uimsbf(8)
    reserved_3 = bslbf(3)
    PCR_PID = uimsbf(13)
    reserved_4 = bslbf(4)
    program_info_length = uimsbf(12)
    descriptors = descriptors(program_info_length)

    @loop(lambda self: self.section_length - (13 + self.program_info_length))
    class maps(Syntax):
        stream_type = uimsbf(8)
        reserved_1 = bslbf(3)
        elementary_PID = uimsbf(13)
        reserved_2 = bslbf(4)
        ES_info_length = uimsbf(12)
        descriptors = descriptors(ES_info_length)

    CRC_32 = rpchof(32)
```

ビット列表記をディスクリプタとして実装したり、繰り返し構造や制御構造をデコレータとして実装したり
することで、なるべく仕様書に近い形でクラスの表記ができるようにしてます。

使い方例1 字幕を表示
```python

import sys

from ariblib import TransportStreamFile
from ariblib.caption import CProfileString
from ariblib.packet import SynchronizedPacketizedElementaryStream
from ariblib.sections import TimeOffsetSection

with TransportStreamFile(sys.argv[1]) as ts:
    SynchronizedPacketizedElementaryStream._pids = [ts.get_caption_pid()]

    # アダプテーションフィールドの PCR の値と、そこから一番近い TOT テーブルの値から、
    # 字幕の表示された時刻を計算します (若干誤差が出ます)
    # PCR が一周した場合の処理は実装されていません
    base_pcr = next(ts.pcrs())
    base_time = next(ts.sections(TimeOffsetSection)).JST_time

    for spes in ts.sections(SynchronizedPacketizedElementaryStream):
        caption_date = base_time + (spes.pts - base_pcr)
        for data in spes.data_units:
            print(caption_date, CProfileString(data.data_unit_data))
```

使い方例2 いま放送中の番組と次の番組を表示
```python

import sys

from ariblib import TransportStreamFile
from ariblib.descriptors import ShortEventDescriptor
from ariblib.sections import EventInformationSection

def show_program(eit):
    event = eit.events.__next__()
    program_title = event.descriptors[ShortEventDescriptor][0].event_name_char
    start = event.start_time
    return "{} {}".format(program_title, start)

with TransportStreamFile(sys.argv[1]) as ts:
    # 自ストリームの現在と次の番組を表示する
    EventInformationSection._table_ids = [0x4E]
    current = next(table for table in ts.sections(EventInformationSection)
                   if table.section_number == 0)
    following = next(table for table in ts.sections(EventInformationSection)
                     if table.section_number == 1)
    print('今の番組', show_program(current))
    print('次の番組', show_program(following))
```

使い方例3: 放送局名の一欄を表示
(地上波ではその局, BSでは全局が表示される)
```python

import sys

from ariblib import TransportStreamFile
from ariblib.constant import SERVICE_TYPES
from ariblib.descriptors import ServiceDescriptor
from ariblib.sections import ServiceDescriptionSection

with TransportStreamFile(sys.argv[1]) as ts:
    for sdt in ts.sections(ServiceDescriptionSection):
        for service in sdt.services:
            for sd in service.descriptors[ServiceDescriptor]:
                print(service.service_id, SERVICE_TYPE[sd.service_type],
                      sd.service_provider_name, sd.service_name)
```

使い方例4: 動画パケットの PID とその動画の解像度を表示
```python

import sys

from ariblib import TransportStreamFile
from ariblib.constants import VIDEO_ENCODE_FORMATS
from ariblib.descriptors import VideoDecodeControlDescriptor
from ariblib.sections import ProgramAssociationSection, ProgramMapSection

with TransportStreamFile(sys.argv[1]) as ts:
    pat = next(ts.sections(ProgramAssociationSection))
    ProgramMapSection._pids = list(pat.pmt_pids)
    for pmt in ts.sections(ProgramMapSection):
        for tsmap in pmt.maps:
            for vd in tsmap.descriptors.get(VideoDecodeControlDescriptor, []):
                print(tsmap.elementary_PID, VIDEO_ENCODE_FORMAT[vd.video_encode_format])
```

使い方例5: EPG情報の表示
```python

import sys

from ariblib import TransportStreamFile
from ariblib.aribstr import AribString
from ariblib.constants import *
from ariblib.descriptors import *
from ariblib.sections import EventInformationSection

with TransportStreamFile(sys.argv[1]) as ts:
    # 表示対象を「自ストリーム、スケジュール」とする
    EventInformationSection._table_ids = range(0x50, 0x60)
    for eit in ts.sections(EventInformationSection):
        for event in eit.events:
            print('service_id', eit.service_id)
            print('event_id:', event.event_id)
            print('start:', event.start_time)
            print('duration:', event.duration)

            desc = event.descriptors
            for sed in desc.get(ShortEventDescriptor, []):
                print('title:', sed.event_name_char)
                print('description:', sed.text_char)
            for cd in desc.get(ComponentDescriptor, []):
                print('video:', COMPONENT_TYPE[cd.stream_content][cd.component_type])
                print('component_text:', cd.component_text)
            for dccd in desc.get(DigitalCopyControlDescriptor, []):
                print('copy:', DIGITAL_RECORDING_CONTROL_TYPE[dccd.copy_control_type])
            for acd in desc.get(AudioComponentDescriptor, []):
                if acd.main_component_flag:
                    print('audio:', COMPONENT_TYPE[acd.stream_content][acd.component_type])
                    print('sampling_rate:', SAMPLING_RATE[acd.sampling_rate])
                    print('audio_text:', acd.audio_text)
                else:
                    print('second_audio:', COMPONENT_TYPE[acd.stream_content][acd.component_type])
                    print('second_sampling_rate:', SAMPLING_RATE[acd.sampling_rate])
                    print('second_audio_text:', acd.audio_text)
            for egd in desc.get(EventGroupDescriptor, []):
                print('group_type:', EVENT_GROUP_TYPE[egd.group_type])
                print('events:', ', '.join('{}={}'.format(e.service_id, e.event_id)
                                           for e in egd.events))
            for ctd in desc.get(ContentDescriptor, []):
                nibble = next(ctd.nibbles)
                print('genre1:', CONTENT_TYPE[nibble.content_nibble_level_1][0])
                print('genre2:', CONTENT_TYPE[nibble.content_nibble_level_1][1]
                                             [nibble.content_nibble_level_2])
            detail = [('', [])]
            for eed in desc.get(ExtendedEventDescriptor, []):
                for item in eed.items:
                    key = item.item_description_char
                    # タイトルが空か一つ前と同じ場合は本文を一つ前のものにつなげる
                    if str(key) == '' or str(detail[-1][0]) == str(key):
                        detail[-1][1].append(item.item_char)
                    else:
                        detail.append((key, [item.item_char]))
            for key, value in detail[1:]:
                print('{}: {}'.format(key, ''.join(map(lambda s: str(s).strip(), value))))
            print('=' * 80)
```
拡張形式イベント記述子の処理のところがいけてないので、なんとかするつもりです。

使い方例6: 深夜アニメの出力
```python

import sys

from ariblib import TransportStreamFile
from ariblib.descriptors import ContentDescriptor, ShortEventDescriptor
from ariblib.sections import EventInformationSection

with TransportStreamFile(sys.argv[1]) as ts:
    EventInformationSection._table_ids = range(0x50, 0x70)
    for eit in ts.sections(EventInformationSection):
        for event in eit.events:
            for genre in event.descriptors.get(ContentDescriptor, []):
                nibble = next(genre.nibbles)
                if nibble.content_nibble_level_1 == 0x07 and not (4 < event.start_time.hour < 22):
                    for sed in event.descriptors.get(ShortEventDescriptor, []):
                        print(eit.service_id, event.event_id, event.start_time,
                              event.duration, sed.event_name_char, sed.text_char)
```

