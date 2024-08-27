/*
osap/packets.cpp

common routines

Jake Read at the Center for Bits and Atoms
(c) Massachusetts Institute of Technology 2021

This work may be reproduced, modified, distributed, performed, and
displayed for any purpose, but must acknowledge the osap project.
Copyright is retained and must be preserved. The work is provided as is;
no warranty is provided, and users accept all liability.
*/

#include "packets.h"
#include "../utils/serdes.h"
#include "../utils/keys.h"
#include "../utils/debug.h"

// we have some file-scoped pointers, 
VPacket* queueStart;
VPacket* firstFree;

// ---------------------------------------------- Stack Utilities 

void stackReset(VPacket* stack, size_t stackSize){
  // reset each individual, 
  for(uint16_t p = 0; p < stackSize; p ++){
    stack[p].len = 0;
    stack[p].vport = nullptr;
    stack[p].linkGateway = nullptr;
    stack[p].runtime = nullptr;
    stack[p].serviceDeadline = 0;
    stack[p].timeOfEntry = 0;
  }
  // set next ptrs, forwards pass
  for(uint16_t p = 0; p < stackSize - 1; p ++){
    stack[p].next = &(stack[p+1]);
  }
  stack[stackSize - 1].next = &(stack[0]);
  // set previous ptrs, reverse pass
  for(uint16_t p = 1; p < stackSize; p ++){
    stack[p].previous = &(stack[p-1]);
  }
  stack[0].previous = &(stack[stackSize - 1]);
  // queueStart element is [0], as is the firstFree, at startup,
  queueStart = &(stack[0]);
  firstFree = &(stack[0]);
}

size_t stackGetPacketsToService(VPacket** packets, size_t maxPackets){
  // this is the zero-packets case;
  if(firstFree == queueStart) return 0;
  // this is how many max we can possibly list,
  uint16_t iters = maxPackets < OSAP_CONFIG_STACK_SIZE ? maxPackets : OSAP_CONFIG_STACK_SIZE;
  // otherwise do...
  VPacket* pck = queueStart;
  uint16_t count = 0;
  for(uint16_t p = 0; p < iters; p ++){
    // stash it in the callers' list, 
    packets[p] = pck;
    // increment, 
    count ++;
    // check next-fullness, 
    // (if packet is allocated to a vport or a linkGateway they would be linked)
    if(pck->next->vport == nullptr && pck->next->linkGateway == nullptr && pck->next->runtime == nullptr){
      // if next is empty, this is final count:
      return count;
    } else {
      // if it ain't, collect next and continue stuffing
      pck = pck->next;
    }
  }
  // TODO: we could have an additional step here of sorting the list 
  // in decending deadline-time order... to manage priorities. we could *also*
  // sort-in-place, i.e. when a call is made to stuff-a-packet, check deadline, 
  // and sort into the linked list there... not a huge lift, just a little linked-list-tricky 
  // for the time being, we're just returning 'em 
  // end-of-loop thru all possible, none free, so:
  return count;
}

// ---------------------------------------------- Stack Allocators 
// TODO: templates would eliminate need for manually overloading each of these, 
// but would need to be careful w/ compiler versions, non ? 

boolean claimPacketCheck(VPort* vport){
  if( firstFree->vport == nullptr && 
      firstFree->linkGateway == nullptr && 
      firstFree->runtime == nullptr && 
      vport->currentPacketHold < vport->maxPacketHold
  ){
    return true;
  } else {
    return false;
  }
}

boolean claimPacketCheck(LinkGateway* linkGateway){
  if( firstFree->vport == nullptr && 
      firstFree->linkGateway == nullptr && 
      firstFree->runtime == nullptr && 
      linkGateway->currentPacketHold < linkGateway->maxPacketHold
  ){
    return true;
  } else {
    return false;
  }
}

boolean claimPacketCheck(OSAP_Runtime* runtime){
  if( firstFree->vport == nullptr && 
      firstFree->linkGateway == nullptr && 
      firstFree->runtime == nullptr && 
      runtime->currentPacketHold < runtime->maxPacketHold
  ){
    return true;
  } else {
    return false;
  }
}

VPacket* claimPacketFromStack(VPort* vport){
  if(claimPacketCheck(vport)){
    // allocate the firstFree in the queue to the requester, 
    VPacket* pck = firstFree;
    pck->vport = vport;
    vport->currentPacketHold ++;
    // increment, 
    firstFree = firstFree->next;
    // hand it over, 
    return pck;
  } else {
    return nullptr;
  }
}

VPacket* claimPacketFromStack(LinkGateway* linkGateway){
  if(claimPacketCheck(linkGateway)){
    VPacket* pck = firstFree;
    pck->linkGateway = linkGateway;
    linkGateway->currentPacketHold ++;
    // increment, 
    firstFree = firstFree->next;
    // hand it over, 
    return pck;
  } else {
    return nullptr;
  }
}

VPacket* claimPacketFromStack(OSAP_Runtime* runtime){
  if(claimPacketCheck(runtime)){
    VPacket* pck = firstFree;
    pck->runtime = runtime;
    runtime->currentPacketHold ++;
    // increment, 
    firstFree = firstFree->next;
    // hand it over, 
    return pck;
  } else {
    return nullptr;
  }
}

void relinquishPacketToStack(VPacket* pck){
  // decriment-count per-point maximums 
  if(pck->vport){
    pck->vport->currentPacketHold --;
  } else if (pck->linkGateway){
    pck->linkGateway->currentPacketHold --;
  } else if (pck->runtime){
    pck->runtime->currentPacketHold --;
  }
  // zero the packet out,
  pck->vport = nullptr;
  pck->linkGateway = nullptr;
  pck->runtime = nullptr;
  // and these, just in case... 
  pck->len = 0;
  pck->serviceDeadline = 0;
  pck->timeOfEntry = 0;

  // now we can handle the stack free-ness, 
  // if it was at the start of the queue, that now 
  // begins at the next packet: 
  if(queueStart == pck){
    queueStart = pck->next;
  } else {
    // otherwise we un-stick it from the middle:
    pck->previous->next = pck->next;
    pck->next->previous = pck->previous;
    // now, insert this where the old firstFree was
    firstFree->previous->next = pck;
    pck->previous = firstFree->previous;
    pck->next = firstFree;
    firstFree->previous = pck;
    // and the item is the new firstFree element,
    firstFree = pck;
  }
}

// ---------------------------------------------- Route Retrieval 

// local ute, this figures where the last byte in the route is 
// in the new scheme, end-of-route is either a SMSG or a DGRM, right ? 
uint8_t routeEndScan(uint8_t* data, size_t maxLen){
  // 1st instruction is at pck[5] since we have | PTR | PHTTL:2 | MSS:2 | 
  uint8_t end = 5;
  uint8_t increment = 0;
  while(true){
    // protocol is such that PKEY == size of that instruction
    increment = data[end] >> 6;
    if(!increment) return end;
    if(increment == 3) return end;
    end += increment;
    if(end > maxLen) return maxLen;
  }
}

void getRouteFromPacket(VPacket* pck, Route* route){
  // ttl, segsize come out of the packet head, 
  // | PTR:1 | SDL:2 | MSS:2 | 
  size_t rptr = 1;
  route->timeToLive = deserializeTight<uint16_t>(pck->data, &rptr);
  route->maxSegmentSize = deserializeTight<uint16_t>(pck->data, &rptr);
  // get end-of-route location 
  uint16_t routeEndLocation = routeEndScan(pck->data, pck->len);
  // now we can memcpy the route's encoded-path section over, 
  memcpy(route->encodedPath, &(pck->data[5]), routeEndLocation - 5);
  // and the length, 
  route->encodedPathLen = routeEndLocation - 5;
}

// ---------------------------------------------- Packet Authorship 

uint16_t stuffPacketRoute(VPacket* pck, Route* route){
  // the pointer is always initialized at 5, 
  //                          V
  // | PTR | SDL:2 | MSS: 2 | 1ST_INSTRUCT 
  pck->data[0] = 5;
  size_t wptr = 1;
  serializeTight<uint16_t>(route->timeToLive, pck->data, &wptr);
  serializeTight<uint16_t>(route->maxSegmentSize, pck->data, &wptr);  
  // and the route, 
  memcpy(pck->data + 5, route->encodedPath, route->encodedPathLen);
  // stuffPacketRoute is called when we mint new packets, effectively 
  // when they are created in our system: 
  pck->timeOfEntry = micros();
  // and a service deadline, sometime in the future: 
  pck->serviceDeadline = pck->timeOfEntry + route->timeToLive;
  // return the end of this chunk, 
  return route->encodedPathLen + 5;
}

// stuffing into allocated packet, 
void stuffPacketRaw(VPacket* pck, Route* route, uint8_t* data, size_t len){
  // write pointer and route-writing, 
  uint16_t wptr = stuffPacketRoute(pck, route);
  // no bigguns... 
  if(len + wptr > route->maxSegmentSize){ 
    OSAP_ERROR("oversize raw-write" + String(wptr + len)); 
    len = 1; 
  }
  // now stuff the data, 
  memcpy(&(pck->data[wptr]), data, len);
  // service deadline was calc'd in stuffPacketRoute, 
  // that'd be it then, 
  pck->len = wptr + len;
  // OSAP_DEBUG(OSAP_DEBUG_PRINT_PACKET(pck));
}

// stuffing from:to port,
void stuffPacketPortToPort(VPacket* pck, Route* route, uint16_t sourcePort, uint16_t destinationPort, uint8_t* data, size_t len){
  // pretty similar to above, 
  uint16_t wptr = stuffPacketRoute(pck, route);
  // guard largess
  if(len + wptr + 5 > route->maxSegmentSize){ 
    OSAP_ERROR("oversize port-write" + String(wptr + len)); 
    len = 1; 
  }
  // author port-key-stuff, 
  pck->data[wptr ++] = PKEY_DGRM << 6 | sourcePort >> 6;
  pck->data[wptr ++] = sourcePort << 2 | destinationPort >> 8;
  pck->data[wptr ++] = destinationPort & 255;
  // and stuff the payload ! 
  memcpy(&(pck->data[wptr]), data, len);
  // aaaaand we're done here... 
  pck->len = len + wptr;
}
