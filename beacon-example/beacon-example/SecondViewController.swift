//
//  SecondViewController.swift
//  beacon-example
//
//  Created by Michael Vartanian on 7/30/18.
//  Copyright © 2018 Michael Vartanian. All rights reserved.
//

import UIKit
import CoreLocation

class SecondViewController: UIViewController, CLLocationManagerDelegate {

    let IBEACON_PROXIMITY_UUID = "74278BDA-B644-4520-8F0C-720EAF059935"
    var locationManager: CLLocationManager!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        locationManager = CLLocationManager()
        locationManager.delegate = self
        locationManager.requestAlwaysAuthorization()
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }

    private func locationManager(manager: CLLocationManager, didChangeAuthorizationStatus status: CLAuthorizationStatus) {
        if !(status == .authorizedAlways || status == .authorizedWhenInUse) {
            print("Must allow location access for this application to work")
        } else {
            if let uuid = NSUUID(uuidString: IBEACON_PROXIMITY_UUID) {
                let beaconRegion = CLBeaconRegion(proximityUUID: uuid as UUID, identifier: "iBeacon")
                startRanging(beaconRegion: beaconRegion)
            }
        }
    }
    
    func startRanging(beaconRegion: CLBeaconRegion) {
        locationManager.startRangingBeacons(in: beaconRegion)
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

