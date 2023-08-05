
import sys, collections
import numpy

import shape, svg

def sketch(item, outname):
    print outname,
    sys.stdout.flush()
    
    item_rot = item.copy()
    item_rot.rotate(1,0,0,-90)
    
    item_iso = item.copy()
    item_iso.rotate(0,0,1,-45)
    item_iso.rotate(1,0,0,-45)
    
    ox = 0
    oy = 0
    
    pic = svg.SVG()
    pic.require(0,0)
        
    for (item,showdim) in [ (item,1), (item_rot,1), (item_iso,0) ]:
        extent = item.extent()
        
        if extent.xmax-extent.xmin < extent.ymax-extent.ymin:
            ox = pic.max_x + 10
            oy = -pic.max_y
        else:
            ox = 0.0
            oy = -(extent.ymax-extent.ymin)-pic.max_y - 20
        
        ox -= extent.xmin
        oy -= extent.ymin
        
        xmid = (extent.xmin+extent.xmax)*0.5
        ymid = (extent.ymin+extent.ymax)*0.5
        zmid = (extent.zmin+extent.zmax)*0.5
        if showdim:
            pic.text(ox+xmid, -oy-extent.ymax-10, '%.1fmm' % (extent.xmax-extent.xmin))
            pic.text(ox+extent.xmax + 5, -oy-ymid, '%.1fmm' % (extent.ymax-extent.ymin))    
            #pic.text(ox+extent.xmin, -oy-extent.ymin+10, '%.1fmm tall' % (extent.zmax-extent.zmin))
            pic.save(outname)
        
        lines = collections.defaultdict(list)
        for tri in item.triangles():
            #a = shape.Loop([ (x,y) for x,y,z in tri ]).area
            #if not a: 
            #    continue
            #if a < 0:
            #    tri = tri[::-1]
                
            a = numpy.array(tri)
            normal = numpy.cross(a[1]-a[0],a[2]-a[0])
            normal /= numpy.sqrt(numpy.dot(normal,normal))
            
            lines[(tri[0],tri[1])].append( normal )
            lines[(tri[1],tri[2])].append( normal )
            lines[(tri[2],tri[0])].append( normal )
    
        for a,b in lines:
            if (b,a) not in lines:
                weight = -1.0
                normals = lines[(a,b)]
            else:
                if (b,a) < (a,b): continue
                normals = lines[(a,b)] + lines[(b,a)]
                
                weight = -1.0
                for n1 in lines[(a,b)]:
                    for n2 in lines[(b,a)]:
                        if n1[2]*n2[2] > 0.0:
                            weight = max(weight, numpy.dot(n1,n2))
            
            weight = (1.0-weight)*0.5                
            if weight < 0.01: continue                
            weight = min(1.0,weight*2)
    
            outs = 0
            ins = 0
            for n in normals:
                if n[2] <= 1e-6:
                    ins += 1
                if n[2] >= -1e-6:
                    outs += 1
            
            if ins >= 2 and not outs:
                weight *= 0.25
            #elif outs >= 2 and not ins:
            #    weight *= 2.0
            
            pic.line([ (ox+x,-oy-y) for x,y,z in [a,b] ],width=0.2 * weight)
        
        #mask = item.polygon_mask()
        #loops = mask.loops()
        #for loop in loops:
        #    pic.polygon([ (ox+x,-oy-y) for x,y in loop ],width=0.2)
        pic.save(outname)
        
        #ox += extent.xmin
        #oy += extent.ymax
        #oy -= extent.ymax-extent.ymin + 40
    
    print


def run(args):
    for filename in args:
        prefix = filename    
        if prefix[-4:].lower() == '.stl': 
            prefix = prefix[:-4]
        outname = prefix + '-sketch.svg'
    
        item = shape.load_stl(filename)

        sketch(item, outname)
        
   
   
if __name__ == '__main__':
    shape.main(run)