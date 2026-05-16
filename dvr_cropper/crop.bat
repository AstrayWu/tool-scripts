ffmpeg -i NO20240925-082139-000628F.MP4 -vcodec copy -acodec copy -ss 00:00:00 -to 00:00:06   NO20240925-082139-000628F_c1.MP4 -y
ffmpeg -i NO20240925-082139-000628F_c1.MP4 -c:v libx264 -crf 24 -vf format=yuv420p -s 1920x1080 NO20240925-082139-000628F_c2.mp4 -y
ffmpeg -i NO20240925-082139-000628F.MP4 -ss 00:00:00 -frames:v 1 c0.jpg -y
ffmpeg -i NO20240925-082139-000628F.MP4 -ss 00:00:03 -frames:v 1 c1.jpg -y
ffmpeg -i NO20240925-082139-000628F.MP4 -ss 00:00:06 -frames:v 1 c2.jpg -y
