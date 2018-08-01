//
//  BeaconRangeViewController.swift
//  beacon-scanner
//
//  Created by Michael Vartanian on 7/31/18.
//  Copyright © 2018 Michael Vartanian. All rights reserved.
//

import UIKit
import CoreLocation

class BeaconRangeViewController: UIViewController, CLLocationManagerDelegate {
    
    let IBEACON_PROXIMITY_UUID = "8D847D20-0116-435F-9A21-2FA79A706D9E"
    var locationManager: CLLocationManager!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        locationManager = CLLocationManager()
        locationManager.delegate = self
        locationManager.requestWhenInUseAuthorization()
        locationManager.requestAlwaysAuthorization()
        print("end of range view load")
    }
    
    override func viewDidAppear(_ animated: Bool) {
        if let uuid = NSUUID(uuidString: IBEACON_PROXIMITY_UUID) {
            print(uuid)
            let beaconRegion = CLBeaconRegion(proximityUUID: uuid as UUID, identifier: "iBeacon")
            startRanging(beaconRegion: beaconRegion)
            print("start ranging...")
        }
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        if let uuid = NSUUID(uuidString: IBEACON_PROXIMITY_UUID) {
            let beaconRegion = CLBeaconRegion(proximityUUID: uuid as UUID, identifier: "iBeacon")
            stopRanging(beaconRegion: beaconRegion)
            print("stop ranging...")
        }
    }

    func startRanging(beaconRegion: CLBeaconRegion) {
        locationManager.startRangingBeacons(in: beaconRegion)
    }
    
    func stopRanging(beaconRegion: CLBeaconRegion) {
        locationManager.stopRangingBeacons(in: beaconRegion)
    }
    
    //  ======== CLLocationManagerDelegate methods ==========
    
    func locationManager(_ manager: CLLocationManager, didRangeBeacons beacons: [CLBeacon], in region: CLBeaconRegion) {
        for beacon in beacons {
            var beaconProximity: String;
            switch (beacon.proximity) {
            case .unknown:
                beaconProximity = "Unknown"
            case .immediate:
                beaconProximity = "Immediate"
            case .near:
                beaconProximity = "Near"
            case .far:
                beaconProximity = "Far"
            }
            print("BEACON RANGED: uuid: \(beacon.proximityUUID.uuidString) major: \(beacon.major)  minor: \(beacon.minor) proximity: \(beaconProximity)")
        }
    }
}

